#this is the main server control program 

#library imports
import uvicorn

#class imports
from server import websocket_endpoint


def run_server():
    while 1:
        #receieving audio from client
        websocket_endpoint()

        #sending audio to the STT program

        #receieving text from STT program

        #sending text query to llm program

        #receiving llm output

        #sending text output to tts

        #recieving tts output mp3 file

        #sending mp3 file to client 




if __name__ == "__main__":
    #starting server
    uvicorn.run("server:app", host="127.0.0.1", port=8000)
    #starting logic 
    run_server()

#Architecture 
#Recieve speech audio from robot 
#sending audio file to STT program 
#recieving text from STT program
#sending text to query to LLM program
#Recieving LLM output from LLM program
#Sending text output to TTS program 
#Sending TTS audio output to mochigo robot using sender program 

#latency is the biggest problem here, need to work on outputting the llm content continuously 
