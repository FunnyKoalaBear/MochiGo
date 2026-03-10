#this is the main server control program 

#importing libraries
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn #used to start the server 
import subprocess
import time

#importing classes 
from ai_pipeline import pipeline, close

#staring server
app = FastAPI()

def setup_tailscale():
    #run this line in a seperate terminal to make server public 
    #tailscale serve http://127.0.0.1:8000
    subprocess.run("tailscale down")
    subprocess.run("tailscale up")
    subprocess.run("tailscale --bg serve http://127.0.0.1:8000")
    subprocess.run("tailscale status")


#switchboard to communicate between the 2 websocket connections 
class Switchboard():

    def __init__(self, ws):
        self.ws = ws

    def switch():
        pass


#end point, route decorator 
#function that manages connection between mochigo client and local server 
@app.websocket("/ws/mochi")
async def websocket_endpoint(websocket: WebSocket):
    
    await websocket.accept()
    print("Connection made at /ws/mochi")

    try:
        while True:
            
            #recieving data
            data = await websocket.receive_text()
            #print(f"Text receieved was {data}")  

            #run ai pipeline
            llmOut = await pipeline(data)
            print(llmOut)


            #use switchboard to send data to google colab computer for tts 


            #recieve speech data from google colab from switchboard 


            #send speech data to mochi
            #need to change llmOut to ttsOut soon 
            await websocket.send_text(llmOut)
    
            #loop back 

    except (WebSocketDisconnect, KeyboardInterrupt):
        print("Server closing.")
        subprocess.run("tailscale down")
        close()
        exit()



#function that manages websocket connection between google colab cloud computer
@app.websocket("/ws/tts")
async def ttsAudio(websocket: WebSocket):
    
    await websocket.accept()
    print("Connection made at /ws/tts")
    time.sleep(1)

    try:
        while True:

            #sending llm output to colab server
            print("Going to send")
            llmOut = "Thats nice to hear, I am glad you had a great day today" 
            await websocket.send_text(llmOut)

            #recieving tts audio data from colab computer 
            dataOut = await websocket.receive_text()
            print(f"Speech data recieved was: {dataOut}")
            
            #switchboard call to send data back to main function

            #loopback
            time.sleep(1)


    except (WebSocketDisconnect, KeyboardInterrupt):
        print("Server closing.")
        subprocess.run("tailscale down")
        close()
        exit()



if __name__ == "__main__":
    #starting server
    setup_tailscale()
    uvicorn.run("server:app", host="0.0.0.0", port=8000)


#run server with
#fastapi dev testServer.py

#right now the server is using switchbord architecture to communicate and pass data betweeen the 2 clients 
#when scaling, switch the queue architecture so tasks in the background are continuously working and not causing any blocking 