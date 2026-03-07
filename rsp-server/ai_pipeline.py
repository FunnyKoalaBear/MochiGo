#this program generates responses to users audio input

#library imports
import asyncio
import threading

#class imports
from LLm.src.test import get_response
from LLm.src.main import RaspberryAgent, query, main

#setting up LLM
agent = RaspberryAgent()    
t = threading.Thread(target=agent.autonomy_loop)
t.start()

async def pipeline(audio: str):
    
    #sending audio to the STT program

    #receieving text from STT program

    #sending & recieving llm program input & output
    print(f"Query question: {audio}")

    # print("Test LLM: ")
    # response = get_response(audio)
    # print(f"LLM response: {response["content"]}")

    print("Main LLM: ")
    response = query(agent, audio)
    print(response)



    #sending text output to tts

    #recieving tts output mp3 file


    # #simulating processing    
    # await asyncio.sleep(1)


    #sending audio file to server 
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
#Recieve speech audio from robot 
#sending audio file to STT program 
#recieving text from STT program
#sending text to query to LLM program
#Recieving LLM output from LLM program
#Sending text output to TTS program 
#Sending TTS audio output to mochigo robot using sender program 


#future improvements
#tts streaming
#llm streaming 
#stt streaming 

#latency is the biggest problem here, need to work on outputting the llm content continuously 
