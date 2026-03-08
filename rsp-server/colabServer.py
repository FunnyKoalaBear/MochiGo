#this is the main server control program 

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn #used to start the server 

from ai_pipeline import pipeline, close

app = FastAPI()

#end point, route decorator 
@app.websocket("/ws")
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
        close()

@app.websocket("ws/tts")
async def ttsAudio(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:

            #testing 
            #recieving data
            data = await websocket.receive_text()

            #sending data back 
            audioOut = await pipeline(data)
            await websocket.send_text(audioOut)



            #actual logic 
            #sending text data to colab computer 


            #recieving tts audio data from colab computer 


            #sending audio back to ai_pipeline 
    
    except WebSocketDisconnect or KeyboardInterrupt:
        print("Server closing.")
        close()





if __name__ == "__main__":
    #starting server
    uvicorn.run("server:app", host="127.0.0.1", port=8000)


#run server with
#fastapi dev testServer.py