#this program generates responses to users audio input

#library imports
import asyncio
import threading

#class imports
from LLm.src.test import get_response
from LLm.src.main import RaspberryAgent, query, main
from STt.src.mp3STT import load, call

#setting up LLM
agent = RaspberryAgent()    
t = threading.Thread(target=agent.autonomy_loop)
t.start()
model = load()
#file = "rsp-server/STt/data/user_query.mp3"
file = "rsp-server/STt/data/user_query.wav"


async def pipeline(wav_bytes: str):
    
    #reconstructing audio bytes to mp3 file
    with open(file, "wb") as f:
        f.write(wav_bytes)
    
    #sending audio to the STT program
    user_query = call(file, model)
    print(f"Query question: {user_query}")


    #sending & recieving llm program input & output
    print("Main LLM: ")
    response = query(agent, user_query)
    print(response)


    #sending llm respnose back to server for STT 
    #audioOut = f"I am doing good!"
    return response


        
def close():
    agent.stop_event.set()
    t.join()
    print("System shutdown.")



if __name__ == "__main__":
    #starting server
    asyncio.run(pipeline("I am doing good"))


#Architecture 
#Start websocket connection between mochigo and local server
#Start websocket connection between local server and google colab server
#Recieve speech audio from robot 
#sending audio file to STT program 
#recieving text from STT program
#sending text to query to LLM program
#Recieving LLM output from LLM program
#Send LLM Text output to server
#Server sends LLM Text output back to local server
#Local server sends LLM Text Output to Google Colab Server for TTS
#TTS program in Google Colab Server produces wav file
#Wav file is compressed to mp3 file 
#Google Colab Server sends mochigo response audio back to local server through websocket
#Local server forwards recieved audio to mochigo through websocket


#future improvements
#tts streaming
#llm streaming 
#stt streaming 

#latency is the biggest problem here, need to work on outputting the llm content continuously 
