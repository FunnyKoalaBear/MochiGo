import asyncio
from websockets.asyncio.client import connect
import time 

async def sendQuery():
    async with connect("ws://127.0.0.1:8000/ws") as websocket:

        while 1:
            #sending
            await websocket.send("Hi bro")

            #recieving
            message = await websocket.recv()
            print(message)

            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(sendQuery())

