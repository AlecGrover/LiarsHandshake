import asyncio
import websockets

API_KEY = "6qkEezDAGMVxwpHSq1jIaVoTrKssa0H53FbqUjFg"

async def test():
    async with websockets.connect(f'wss://s4101.nyc3.piesocket.com/v3/1?api_key={API_KEY}&notify_self') as websocket:
        await websocket.send("hello")
        response = await websocket.recv()
        print(response)

asyncio.get_event_loop().run_until_complete(test())
