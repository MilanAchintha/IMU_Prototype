
import asyncio
import websockets

async def handle_client(websocket):
    print("ESP32 connected!")

    try:
        async for message in websocket:

            print("Received from ESP32:", message)

            # Send a reply to ESP32
            await websocket.send("Hello from Python!")

    except websockets.exceptions.ConnectionClosed:
        print("ESP32 disconnected")


async def main():

    print("WebSocket server starting...")

    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        8080
    ):
        print("WebSocket server running on port 8080")

        await asyncio.Future()


asyncio.run(main())
