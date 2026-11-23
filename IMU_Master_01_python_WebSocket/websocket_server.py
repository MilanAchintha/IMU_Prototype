
import asyncio
import websockets

# =====================================
# CONFIGURATION
# =====================================

HOST = "0.0.0.0"
PORT = 8080

PACKET_SIZE = 24
BATCH_SIZE = 100

EXPECTED_BATCH_SIZE = PACKET_SIZE * BATCH_SIZE

# Statistics for each ESP32 device
device_stats = {}

# Track connected ESP32 clients
connected_clients = set()


# =====================================
# DEVICE STATISTICS
# =====================================

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
# PROCESS ONE PACKET
# =====================================

def process_packet(packet):

    if len(packet) != PACKET_SIZE:
        print("Invalid packet size:", len(packet))
        return

    # Extract Device ID
    device_id = packet[0]

    # Extract Message ID (4 bytes, little-endian)
    message_id = int.from_bytes(
        packet[1:5],
        byteorder="little",
        signed=False
    )

    stats = get_device_stats(device_id)

    stats["received"] += 1

    last_id = stats["last_message_id"]

    # First packet from this device
    if last_id is None:

        # Assumes message IDs start at zero
        if message_id > 0:
            stats["missing"] += message_id

        stats["last_message_id"] = message_id

        return device_id, message_id

    # Calculate expected next message ID
    expected_id = (last_id + 1) & 0xFFFFFFFF

    if message_id == expected_id:

        # Correct sequence
        pass

    elif message_id == last_id:

        # Duplicate packet
        stats["duplicates"] += 1

    elif ((message_id - expected_id) & 0xFFFFFFFF) < 0x80000000:

        # Missing packets
        missing_count = (
            message_id - expected_id
        ) & 0xFFFFFFFF

        stats["missing"] += missing_count

    else:

        # Older or out-of-order packet
        stats["out_of_order"] += 1

    # Update latest message ID only for newer packets
    if (
        message_id != last_id
        and ((message_id - last_id) & 0xFFFFFFFF) < 0x80000000
    ):
        stats["last_message_id"] = message_id

    return device_id, message_id


# =====================================
# PRINT STATISTICS
# =====================================

def print_statistics():

    print("\n========== DATA LOSS STATISTICS ==========")

    total_received = 0
    total_missing = 0
    total_duplicates = 0
    total_out_of_order = 0

    for device_id, stats in sorted(device_stats.items()):

        print(f"\nDevice ID             : {device_id}")
        print(f"Packets received      : {stats['received']}")
        print(f"Missing packets       : {stats['missing']}")
        print(f"Duplicate packets     : {stats['duplicates']}")
        print(f"Out-of-order packets  : {stats['out_of_order']}")
        print(f"Batches received      : {stats['batches_received']}")
        print(f"Last message ID       : {stats['last_message_id']}")

        total_received += stats["received"]
        total_missing += stats["missing"]
        total_duplicates += stats["duplicates"]
        total_out_of_order += stats["out_of_order"]

    print("\n---------- TOTAL STATISTICS ----------")

    print(f"Total packets received     : {total_received}")
    print(f"Total missing packets      : {total_missing}")
    print(f"Total duplicate packets    : {total_duplicates}")
    print(f"Total out-of-order packets : {total_out_of_order}")

    print("==========================================\n")


# =====================================
# WEBSOCKET CLIENT HANDLER
# =====================================

async def websocket_handler(websocket):

    client_address = websocket.remote_address

    connected_clients.add(client_address)

    print("\n======================================")
    print("ESP32 WebSocket client connected")
    print("Client address:", client_address)
    print("Connected clients:", len(connected_clients))
    print("======================================")

    try:

        async for message in websocket:

            # Expect binary data
            if not isinstance(message, bytes):

                print("Received non-binary message")
                continue

            received_size = len(message)

            # Validate batch size
            if received_size != EXPECTED_BATCH_SIZE:

                print(
                    f"INVALID BATCH SIZE: "
                    f"Expected {EXPECTED_BATCH_SIZE} bytes, "
                    f"Received {received_size} bytes"
                )

                continue

            # One complete batch received
            print(
                f"\nReceived batch: {received_size} bytes "
                f"({BATCH_SIZE} packets)"
            )

            # Process 100 packets
            for i in range(BATCH_SIZE):

                start = i * PACKET_SIZE
                end = start + PACKET_SIZE

                packet = message[start:end]

                result = process_packet(packet)

                if result is not None:

                    device_id, message_id = result

                    print(
                        f"Device ID: {device_id} | "
                        f"Message ID: {message_id}"
                    )

            # Identify device from first packet in batch
            device_id = message[0]

            stats = get_device_stats(device_id)
            stats["batches_received"] += 1

            # Print updated statistics
            print_statistics()

    except websockets.exceptions.ConnectionClosed:

        print("\nWebSocket connection closed:", client_address)

    finally:

        connected_clients.discard(client_address)

        print("Connected clients:", len(connected_clients))


# =====================================
# MAIN SERVER
# =====================================

async def main():

    print("======================================")
    print(" MULTI-ESP32 WEBSOCKET SERVER")
    print("======================================")

    print("Server IP       : 0.0.0.0")
    print("Server Port     :", PORT)
    print("Packet Size     :", PACKET_SIZE, "bytes")
    print("Batch Size      :", BATCH_SIZE, "packets")
    print("Expected Batch  :", EXPECTED_BATCH_SIZE, "bytes")

    print("\nWaiting for ESP32 devices...")

    async with websockets.serve(
        websocket_handler,
        HOST,
        PORT,
        max_size=EXPECTED_BATCH_SIZE
    ):

        await asyncio.Future()


# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nServer stopped by user.")

