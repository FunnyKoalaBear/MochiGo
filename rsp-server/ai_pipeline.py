#this is the main server control program 

#library imports
import uvicorn
import asyncio

#class imports


async def pipeline(audio: str):

    #sending audio to the STT program

    #receieving text from STT program

    #sending text query to llm program

    #receiving llm output

    #sending text output to tts

    #recieving tts output mp3 file

    #simulating processing    
    await asyncio.sleep(1)
    
    #sending audio file to server 
    audioOut = f"I am doing good!"
    return audioOut


if __name__ == "__main__":
    #starting server
    uvicorn.run("server:app", host="127.0.0.1", port=8000)


#Architecture 
#Recieve speech audio from robot 
#sending audio file to STT program 
#recieving text from STT program
#sending text to query to LLM program
#Recieving LLM output from LLM program
#Sending text output to TTS program 
#Sending TTS audio output to mochigo robot using sender program 

#latency is the biggest problem here, need to work on outputting the llm content continuously 
