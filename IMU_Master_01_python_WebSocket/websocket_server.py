
# import asyncio
# import websockets

# async def handle_client(websocket):
#     print("ESP32 connected!")

#     try:
#         async for message in websocket:

#             print("Received from ESP32:", message)

#             # Send a reply to ESP32
#             await websocket.send("Hello from Python!")

#     except websockets.exceptions.ConnectionClosed:
#         print("ESP32 disconnected")


# async def main():

#     print("WebSocket server starting...")

#     async with websockets.serve(
#         handle_client,
#         "0.0.0.0",
#         8080
#     ):
#         print("WebSocket server running on port 8080")

#         await asyncio.Future()


# asyncio.run(main())



import asyncio
import websockets
import struct

async def handle_client(websocket):

    print("ESP32 connected!")

    async for packet in websocket:

        # Check packet size
        if len(packet) != 24:
            print("Invalid packet size:", len(packet))
            continue

        # Device ID: 1 byte
        device_id = packet[0]

        # Message ID: 4 bytes (Little Endian)
        message_id = struct.unpack_from("<I", packet, 1)[0]

        # Temperature: 1 signed byte
        temperature = struct.unpack_from("<b", packet, 5)[0]

        # Accelerometer, Gyroscope, Magnetometer:
        # 9 signed 16-bit values
        sensor_values = struct.unpack_from("<9h", packet, 6)

        accel_x, accel_y, accel_z = sensor_values[0:3]

        gyro_x, gyro_y, gyro_z = sensor_values[3:6]

        mag_x, mag_y, mag_z = sensor_values[6:9]

        print("\n----- RECEIVED IMU DATA -----")

        print("Device ID:", device_id)
        print("Message ID:", message_id)
        print("Temperature:", temperature)

        print("Accelerometer:", accel_x, accel_y, accel_z)
        print("Gyroscope:", gyro_x, gyro_y, gyro_z)
        print("Magnetometer:", mag_x, mag_y, mag_z)

        print("-----------------------------")


async def main():

    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        8080
    ):
        print("WebSocket server started on port 8080")

        await asyncio.Future()


asyncio.run(main())
