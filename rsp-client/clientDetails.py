import asyncio
from websockets.asyncio.client import connect


class WSClient:

    def __init__(self, url: str):
        self.url = url
        self.websocket = None


    async def connect(self):
        self.websocket = await connect(self.url)
        print("Connected!")


    async def send(self, text: str):
        await self.websocket.send(text)


    async def recv(self):
        return await self.websocket.recv()


    async def sendAudio(self, audio_bytes): 
        #need to convert numpy array into bytes first 
        await self.websocket.send(audio_bytes)
        print("Audio sent!")


    async def sendWav(self, file):
        with open(file, "rb") as f:
            wav_bytes = f.read()
        
        await self.websocket.send(wav_bytes)
        print("WAV file sent")

# async def main():

#     client = WSClient("ws://127.0.0.1:8000/ws")

#     await client.connect()

#     await client.send("Hello")
#     msg = await client.recv()

#     print(msg)


# if __name__ == "__main__":
#     asyncio.run(main())