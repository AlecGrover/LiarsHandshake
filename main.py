import asyncio
import websockets

async def hello():
    async with websockets.connect("ws://localhost:80") as websocket:
        await websocket.send("Hello World!")
        await websocket.recv()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(hello())
    