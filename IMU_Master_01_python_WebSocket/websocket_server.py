import asyncio
import websockets
import os
import csv
import time

from datetime import datetime


# ==================================================
# 1. CONFIGURATION
# ==================================================

HOST = "0.0.0.0"
PORT = 8080

# Change this value when adding or removing devices.
DEVICE_COUNT = 2

PACKET_SIZE = 24
BATCH_SIZE = 100

EXPECTED_BATCH_SIZE = PACKET_SIZE * BATCH_SIZE

DATA_FOLDER = "device_data"

# CSV writer settings
QUEUE_MAX_SIZE = 50000
WRITER_BATCH_SIZE = 500
WRITER_WAIT_TIME = 1.0


# ==================================================
# 2. DEVICE STATISTICS
# ==================================================

device_stats = {}

#Initialize statistics for every configured ESP32.
def initialize_devices():

    for device_id in range(1, DEVICE_COUNT + 1):

        device_stats[device_id] = {
            "received": 0,
            "missing": 0,
            "duplicates": 0,
            "out_of_order": 0,
            "last_message_id": None,
            "batches_received": 0,
            "record_number": 0
        }


def get_device_stats(device_id):

    return device_stats[device_id]


# ==================================================
# 3. CSV FILE CONFIGURATION
# ==================================================

CSV_HEADERS = [
    "No.",
    "Message ID",
    "Status",
    "Missing Count",
    "Received Time",
    "Client Address"
]


def get_csv_filename(device_id):

    return os.path.join(
        DATA_FOLDER,
        f"Device_{device_id}.csv"
    )


def initialize_csv_files():

    os.makedirs(DATA_FOLDER, exist_ok=True)

    for device_id in device_stats:

        filename = get_csv_filename(device_id)

        if not os.path.exists(filename) or os.path.getsize(filename) == 0:

            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)
                writer.writerow(CSV_HEADERS)

    print("CSV files initialized.")


# ==================================================
# 4. MESSAGE ID PROCESSING
# ==================================================

def process_packet(packet, client_address):

    if len(packet) != PACKET_SIZE:
        return None

    device_id = packet[0]

    # Accept only configured device IDs.
    if device_id not in device_stats:
        print("Unknown Device ID:", device_id)
        return None

    # Message ID: 4 bytes, little-endian.
    message_id = int.from_bytes(
        packet[1:5],
        byteorder="little",
        signed=False
    )

    stats = get_device_stats(device_id)

    stats["received"] += 1

    last_id = stats["last_message_id"]

    status = "OK"
    missing_count = 0

    # ----------------------------------------------
    # First received packet
    # ----------------------------------------------

    if last_id is None:

        if message_id == 0:
            status = "FIRST"

        else:
            status = "MISSING"
            missing_count = message_id

            stats["missing"] += missing_count

        stats["last_message_id"] = message_id

    # ----------------------------------------------
    # Subsequent packets
    # ----------------------------------------------

    else:

        expected_id = (last_id + 1) & 0xFFFFFFFF

        difference = (message_id - last_id) & 0xFFFFFFFF

        if difference == 0:

            status = "DUPLICATE"
            stats["duplicates"] += 1

        elif difference == 1:

            status = "OK"
            stats["last_message_id"] = message_id

        elif difference < 0x80000000:

            missing_count = difference - 1

            status = "MISSING"

            stats["missing"] += missing_count

            stats["last_message_id"] = message_id

        else:

            status = "OUT_OF_ORDER"

            stats["out_of_order"] += 1

    # ----------------------------------------------
    # Prepare CSV record
    # ----------------------------------------------

    stats["record_number"] += 1

    record = [
        stats["record_number"],
        message_id,
        status,
        missing_count,
        datetime.now().isoformat(timespec="milliseconds"),
        str(client_address)
    ]

    return device_id, record


# ==================================================
# 5. CSV WRITER
# ==================================================

def write_records_to_csv(records):

    """
    This function runs in a separate worker thread.

    Records are grouped by device and written to
    their respective CSV files.
    """

    grouped_records = {}

    for device_id, record in records:

        if device_id not in grouped_records:
            grouped_records[device_id] = []

        grouped_records[device_id].append(record)

    for device_id, device_records in grouped_records.items():

        filename = get_csv_filename(device_id)

        with open(
            filename,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerows(device_records)

            # Push buffered data to the operating system.
            file.flush()

            # Request durable disk synchronization.
            os.fsync(file.fileno())


async def csv_writer_worker(data_queue):

    print("CSV writer started.")

    while True:

        first_item = await data_queue.get()

        if first_item is None:

            data_queue.task_done()
            break

        records = [first_item]

        stopping = False

        # Collect a group of records before writing.
        while len(records) < WRITER_BATCH_SIZE:

            try:

                item = await asyncio.wait_for(
                    data_queue.get(),
                    timeout=WRITER_WAIT_TIME
                )

            except asyncio.TimeoutError:

                break

            if item is None:

                data_queue.task_done()
                stopping = True
                break

            records.append(item)

        # Retry if a CSV write fails.
        while True:

            try:

                await asyncio.to_thread(
                    write_records_to_csv,
                    records
                )

                break

            except Exception as error:

                print("\nCSV WRITE ERROR:", error)
                print("Retrying in 2 seconds...")

                await asyncio.sleep(2)

        # Mark records as completed only after writing.
        for _ in records:
            data_queue.task_done()

        if stopping:
            break

    print("CSV writer stopped.")


# ==================================================
# 6. PRINT STATISTICS
# ==================================================

def print_statistics():

    print("\n========== DEVICE STATISTICS ==========")

    for device_id, stats in device_stats.items():

        print(f"\nDevice ID            : {device_id}")
        print(f"Packets received     : {stats['received']}")
        print(f"Missing packets      : {stats['missing']}")
        print(f"Duplicates           : {stats['duplicates']}")
        print(f"Out of order         : {stats['out_of_order']}")
        print(f"Batches received     : {stats['batches_received']}")
        print(f"Last message ID      : {stats['last_message_id']}")

    print("========================================\n")



last_print_time = 0.0


def maybe_print_statistics():

    global last_print_time

    now = time.time()

    if now - last_print_time >= 5.0:

        print_statistics()

        last_print_time = now


# ==================================================
# 7. WEBSOCKET HANDLER
# ==================================================

async def websocket_handler(websocket):

    client_address = websocket.remote_address

    connection_devices = set()

    print("\n====================================")
    print("ESP32 CONNECTED")
    print("Client:", client_address)
    print("====================================")

    try:

        async for message in websocket:

            if not isinstance(message, bytes):

                print("ERROR: Non-binary message received")
                continue

            if len(message) != EXPECTED_BATCH_SIZE:

                print(
                    "INVALID BATCH SIZE:",
                    len(message),
                    "Expected:",
                    EXPECTED_BATCH_SIZE
                )

                continue

            batch_devices = set()

            # Process all packets in the received batch.
            for i in range(BATCH_SIZE):

                start = i * PACKET_SIZE
                end = start + PACKET_SIZE

                packet = message[start:end]

                result = process_packet(
                    packet,
                    client_address
                )

                if result is None:
                    continue

                device_id, record = result

                await data_queue.put((device_id, record))

                batch_devices.add(device_id)
                connection_devices.add(device_id)

            # Count one batch for each device present.
            for device_id in batch_devices:

                device_stats[device_id]["batches_received"] += 1

            # Prints only once every 5 seconds
            maybe_print_statistics()

    except websockets.exceptions.ConnectionClosed as error:

        print("WebSocket connection closed:", error)

    except Exception as error:

        print("WebSocket handler error:", error)

    finally:

        print("\nESP32 DISCONNECTED:", client_address)

        print("Devices seen on this connection:", connection_devices)

# ==================================================
# 8. MAIN SERVER
# ==================================================

async def main():

    global data_queue

    print("======================================")
    print("     MULTI-ESP32 DATA SERVER")
    print("======================================")

    print("Server IP       :", HOST)
    print("Server Port     :", PORT)
    print("Device Count    :", DEVICE_COUNT)
    print("Packet Size     :", PACKET_SIZE)
    print("Batch Size      :", BATCH_SIZE)
    print("Expected Batch  :", EXPECTED_BATCH_SIZE)

    print("CSV Folder      :", os.path.abspath(DATA_FOLDER))

    # Initialize configured devices.
    initialize_devices()

    # Create CSV files.
    initialize_csv_files()

    # Central queue for all device records.
    data_queue = asyncio.Queue(
        maxsize=QUEUE_MAX_SIZE
    )

    # Start one independent CSV writer.
    writer_task = asyncio.create_task(
        csv_writer_worker(data_queue)
    )

    print("\nWaiting for ESP32 devices...")

    try:

        async with websockets.serve(
            websocket_handler,
            HOST,
            PORT,
            max_size=EXPECTED_BATCH_SIZE,
            max_queue=8
        ):

            await asyncio.Future()

    finally:

        print("\nStopping server...")

        # Wait until queued records are written.
        await data_queue.join()

        # Tell the writer to finish.
        await data_queue.put(None)

        await writer_task

        print("\nAll queued records have been written.")
        print_statistics()


# ==================================================
# 9. START SERVER
# ==================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nServer stopped by user.")


