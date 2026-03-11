#this program needs to send and receive audio i/o data bewteeen client and server

# HTTP → prompts
# HTTP streaming → AI responses
# WebSocket → audio

#library imports
import asyncio
import subprocess
import sys, os 


#class imports
from voiceIn import Audio
from clientDetails import WSClient
import time
from audio import record, playback
sys.path.append(os.path.abspath("../rsp-server/STT"))
from src.mp3STT import load, call


audio = Audio()
# wsclient = WSClient("ws://127.0.0.1:8000/ws/mochi")
wsclient = WSClient("ws://note-d1.tail8b0d7e.ts.net:8000/ws/mochi")

#start tailscale before running program
#tailscale up in terminal
subprocess.run("tailscale up")


cloudClient = WSClient("")
file = "rsp-client/Audio_Output/tts_out.mp3"

async def run_mochigo():

    #making connection
    await wsclient.connect()

    while 1:
        #wait for wake() function to return true
        await asyncio.to_thread(audio.wake)


        #recieve audio file from voiceIn.py
        # try:
        #     voiceInput = await asyncio.to_thread(audio.record)
        # except:
        #     print("Could not recieve audio input, restarting loop")
        #     continue
        record()

        #STT on audio file 
        voiceInput = "STT Output"


        #send audio file to server 
        await wsclient.send(voiceInput)
        print("sent")


        #recieve audio output from server and save it as an mp3 file
        await wsclient.recvAudio()


        #play the audio output file 
        playback()


        #network flush and loopback 
        await asyncio.sleep(0.01)



if __name__ == "__main__":
    try:
        model = load()
        asyncio.run(run_mochigo())
    except KeyboardInterrupt:
        print("\nShutting down MochiGo...")

        #closing tailscape
        subprocess.run("tailscale down")


#Pipeline
#Wait for wake function
#Recieve audio file from voiceIn.py
#Send audio input to server 
#Recieve audio output from server
#Make voiceOut.py play audio output on speakers  
