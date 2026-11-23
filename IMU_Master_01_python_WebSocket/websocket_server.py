
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

# Track statistics separately for each device
device_stats = {}


def get_device_stats(device_id):

    if device_id not in device_stats:

        device_stats[device_id] = {
            "received": 0,
            "missing": 0,
            "duplicates": 0,
            "out_of_order": 0,
            "last_message_id": None
        }

    return device_stats[device_id]


def process_packet(packet):

    if len(packet) != PACKET_SIZE:
        print("Invalid packet size:", len(packet))
        return

    # Extract device ID
    device_id = packet[0]

    # Extract 4-byte message ID (little-endian)
    message_id = int.from_bytes(
        packet[1:5],
        byteorder="little",
        signed=False
    )

    stats = get_device_stats(device_id)

    stats["received"] += 1

    last_id = stats["last_message_id"]

    if last_id is None:

        # First packet received.
        # Establish the starting sequence number.
        # Do not count earlier message IDs as lost.
        stats["last_message_id"] = message_id
        return device_id, message_id

    else:

        expected_id = (last_id + 1) & 0xFFFFFFFF

        if message_id == expected_id:
            pass

        elif message_id == last_id:
            stats["duplicates"] += 1

        elif ((message_id - expected_id) & 0xFFFFFFFF) < 0x80000000:

            # Forward sequence gap
            missing_count = (
                message_id - expected_id
            ) & 0xFFFFFFFF

            stats["missing"] += missing_count

        else:

            # Older or out-of-order packet
            stats["out_of_order"] += 1

    # Keep the latest observed message ID
    if last_id is None or (
        ((message_id - last_id) & 0xFFFFFFFF) < 0x80000000
        and message_id != last_id
    ):
        stats["last_message_id"] = message_id

    return device_id, message_id


def print_statistics():

    print("\n========== DATA LOSS STATISTICS ==========")

    for device_id, stats in device_stats.items():

        print(f"\nDevice ID             : {device_id}")
        print(f"Packets received      : {stats['received']}")
        print(f"Missing packets       : {stats['missing']}")
        print(f"Duplicate packets     : {stats['duplicates']}")
        print(f"Out-of-order packets  : {stats['out_of_order']}")

    print("==========================================\n")


async def websocket_handler(websocket):

    client_address = websocket.remote_address

    print("\nWebSocket client connected:", client_address)

    try:

        async for message in websocket:

            # We expect binary messages
            if not isinstance(message, bytes):
                print("Received non-binary message")
                continue

            received_size = len(message)

            # Check batch size
            if received_size != EXPECTED_BATCH_SIZE:

                print(
                    f"INVALID BATCH SIZE: "
                    f"Expected {EXPECTED_BATCH_SIZE} bytes, "
                    f"Received {received_size} bytes"
                )

                continue

            print(
                f"\nReceived batch: {received_size} bytes "
                f"({BATCH_SIZE} packets)"
            )

            # Process all 100 packets
            for i in range(BATCH_SIZE):

                start = i * PACKET_SIZE
                end = start + PACKET_SIZE

                packet = message[start:end]

                result = process_packet(packet)

                if result is not None:

                    device_id, message_id = result

                    print(
                        f"Device: {device_id} | "
                        f"Message ID: {message_id}"
                    )

            # Print statistics after each batch
            print_statistics()

    except websockets.exceptions.ConnectionClosed:
        print("WebSocket client disconnected:", client_address)


async def main():

    print("Starting WebSocket server...")
    print("Listening on:", HOST, PORT)
    print("Packet size:", PACKET_SIZE)
    print("Batch size:", BATCH_SIZE)
    print("Expected message size:", EXPECTED_BATCH_SIZE)

    async with websockets.serve(
        websocket_handler,
        HOST,
        PORT,
        max_size=EXPECTED_BATCH_SIZE
    ):

        print("\nWaiting for ESP32 connection...")

        await asyncio.Future()


if __name__ == "__main__":

    asyncio.run(main())
