from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn #used to start the server 

app = FastAPI()

#end point, route decorator 
#does  GET http://localhost:8000/

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        #recieving data
        data = await websocket.receive_text()

        #sending data back 
        await websocket.send_text(f"Message text was: {data} dayumm")
        
        #computing data
        if data == "die":
            exit()
        
        #printing receieved data
        print(f"Text receieved was {data}")        

        #loop back 



if __name__ == "__main__":
    #starting server
    uvicorn.run("server:app", host="127.0.0.1", port=8000)


#run server with
#fastapi dev testServer.py