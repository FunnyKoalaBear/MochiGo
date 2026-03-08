#this is the main server control program 

#importing libraries
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn #used to start the server 
import subprocess

#importing classes 
from ai_pipeline import pipeline, close

#staring server
app = FastAPI()

#run this line in a seperate terminal to make server public 
#tailscale serve http://127.0.0.1:8000
subprocess.run("tailscale down")
subprocess.run("tailscale up")
subprocess.run("tailscale --bg serve http://127.0.0.1:8000")
subprocess.run("tailscale status")

#end point, route decorator 
@app.websocket("/ws/mochi")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            
            #recieving data
            data = await websocket.receive_text()
            #print(f"Text receieved was {data}")  

            #run ai pipeline
            audioOut = await pipeline(data)
            print(audioOut)

            #sending data back 
            await websocket.send_text(audioOut)
    
            #loop back 

    except WebSocketDisconnect or KeyboardInterrupt:
        print("Server closing.")
        subprocess.run("tailscale down")
        close()

@app.websocket("/ws/tts")
async def ttsAudio(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            #sending text data to colab computer 
            pass

            #recieving tts audio data from colab computer 


            #sending audio back to ai_pipeline 
    
    except:
        pass



if __name__ == "__main__":
    #starting server
    uvicorn.run("server:app", host="0.0.0.0", port=8000)


#run server with
#fastapi dev testServer.py

#right now the server is using switchbord architecture to communicate and pass data betweeen the 2 clients 
#when scaling, switch the queue architecture so tasks in the background are continuously working and not causing any blocking 