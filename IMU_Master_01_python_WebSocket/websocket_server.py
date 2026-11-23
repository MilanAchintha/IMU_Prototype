
import asyncio
import websockets
import os

from openpyxl import Workbook


# =====================================
# CONFIGURATION
# =====================================

HOST = "0.0.0.0"
PORT = 8080

PACKET_SIZE = 24
BATCH_SIZE = 100

EXPECTED_BATCH_SIZE = PACKET_SIZE * BATCH_SIZE

EXCEL_SAVE_INTERVAL = 5


# =====================================
# CREATE TWO EXCEL WORKBOOKS
# =====================================

device_workbooks = {}

HEADERS = [
    "No.",
    "Message ID",
    "Status",
    "Missing Count"
]


def create_device_workbook(device_id):

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = f"Device_{device_id}"

    sheet.append(HEADERS)

    device_workbooks[device_id] = workbook

    return workbook


# Create both workbooks immediately
create_device_workbook(1)
create_device_workbook(2)


# =====================================
# SAVE EXCEL FILE
# =====================================

def save_device_excel(device_id):

    filename = f"Device_{device_id}_message_ids.xlsx"

    try:

        device_workbooks[device_id].save(filename)

        print(f"Device {device_id} Excel saved: {filename}")

    except PermissionError:

        print(f"ERROR: Close {filename} in Excel before saving.")

    except Exception as error:

        print(f"Device {device_id} save error:", error)


def save_all_excel_files():

    print("\n========== SAVING EXCEL FILES ==========")

    for device_id in (1, 2):

        save_device_excel(device_id)

    print("========================================\n")


# =====================================
# DEVICE STATISTICS
# =====================================

device_stats = {}


def get_device_stats(device_id):

    if device_id not in device_stats:

        device_stats[device_id] = {
            "received": 0,
            "missing": 0,
            "duplicates": 0,
            "out_of_order": 0,
            "last_message_id": None,
            "batches_received": 0
        }

    return device_stats[device_id]


# =====================================
# PROCESS PACKET
# =====================================

def process_packet(packet):

    if len(packet) != PACKET_SIZE:
        print("Invalid packet size:", len(packet))
        return None

    # Device ID
    device_id = packet[0]

    if device_id not in (1, 2):
        print("Unknown Device ID:", device_id)
        return None

    # Message ID (4 bytes, little-endian)
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

    # =====================================
    # CHECK MESSAGE ID
    # =====================================

    if last_id is None:

        if message_id == 0:
            status = "FIRST"

        else:
            status = "MISSING"
            missing_count = message_id
            stats["missing"] += missing_count

        stats["last_message_id"] = message_id

    else:

        expected_id = (last_id + 1) & 0xFFFFFFFF

        if message_id == expected_id:

            status = "OK"

        elif message_id == last_id:

            status = "DUPLICATE"
            stats["duplicates"] += 1

        elif ((message_id - expected_id) & 0xFFFFFFFF) < 0x80000000:

            missing_count = (
                message_id - expected_id
            ) & 0xFFFFFFFF

            status = "MISSING"
            stats["missing"] += missing_count

            stats["last_message_id"] = message_id

        else:

            status = "OUT_OF_ORDER"
            stats["out_of_order"] += 1

        if (
            message_id != last_id
            and ((message_id - last_id) & 0xFFFFFFFF) < 0x80000000
        ):

            stats["last_message_id"] = message_id

    # =====================================
    # WRITE TO CORRECT EXCEL FILE
    # =====================================

    workbook = device_workbooks[device_id]

    sheet = workbook[f"Device_{device_id}"]

    row_number = sheet.max_row

    sheet.append([
        row_number,
        message_id,
        status,
        missing_count
    ])

    return device_id


# =====================================
# PRINT STATISTICS
# =====================================

def print_statistics():

    print("\n========== DATA LOSS STATISTICS ==========")

    for device_id in (1, 2):

        stats = get_device_stats(device_id)

        print(f"\nDevice ID             : {device_id}")
        print(f"Packets received      : {stats['received']}")
        print(f"Missing packets       : {stats['missing']}")
        print(f"Duplicate packets     : {stats['duplicates']}")
        print(f"Out-of-order packets  : {stats['out_of_order']}")
        print(f"Batches received      : {stats['batches_received']}")
        print(f"Last message ID       : {stats['last_message_id']}")

    print("==========================================\n")


# =====================================
# AUTOMATIC EXCEL SAVING
# =====================================

async def periodic_excel_save():

    while True:

        await asyncio.sleep(EXCEL_SAVE_INTERVAL)

        print("\nAutomatic Excel save...")

        save_all_excel_files()


# =====================================
# WEBSOCKET HANDLER
# =====================================

async def websocket_handler(websocket):

    client_address = websocket.remote_address

    connection_devices = set()

    print("\n======================================")
    print("ESP32 CONNECTED")
    print("Client address:", client_address)
    print("======================================")

    try:

        async for message in websocket:

            if not isinstance(message, bytes):

                print("Received non-binary message")
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

            # Process all 100 packets
            for i in range(BATCH_SIZE):

                start = i * PACKET_SIZE
                end = start + PACKET_SIZE

                packet = message[start:end]

                device_id = process_packet(packet)

                if device_id is not None:

                    batch_devices.add(device_id)
                    connection_devices.add(device_id)

            # Update batch count
            for device_id in batch_devices:

                stats = get_device_stats(device_id)

                stats["batches_received"] += 1

                print(
                    f"Received {BATCH_SIZE} packets "
                    f"from Device {device_id}"
                )

            print_statistics()

    except websockets.exceptions.ConnectionClosed:

        print("\nWebSocket connection closed:", client_address)

    finally:

        print("\nESP32 DISCONNECTED:", client_address)

        # Save the files belonging to this connection
        for device_id in connection_devices:

            save_device_excel(device_id)


# =====================================
# MAIN SERVER
# =====================================

async def main():

    print("======================================")
    print(" MULTI-ESP32 WEBSOCKET SERVER")
    print("======================================")

    print("Server IP       :", HOST)
    print("Server Port     :", PORT)
    print("Packet Size     :", PACKET_SIZE)
    print("Batch Size      :", BATCH_SIZE)
    print("Expected Batch  :", EXPECTED_BATCH_SIZE)

    print("\nExcel save interval:", EXCEL_SAVE_INTERVAL, "seconds")
    print("Excel folder:", os.getcwd())

    # Create both Excel files immediately
    save_all_excel_files()

    # Start automatic saving
    save_task = asyncio.create_task(periodic_excel_save())

    print("\nWaiting for ESP32 devices...")

    try:

        async with websockets.serve(
            websocket_handler,
            HOST,
            PORT,
            max_size=EXPECTED_BATCH_SIZE
        ):

            await asyncio.Future()

    finally:

        save_task.cancel()

        try:
            await save_task
        except asyncio.CancelledError:
            pass

        print("\nStopping server...")

        save_all_excel_files()


# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nServer stopped by user.")
