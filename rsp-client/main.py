#this program needs to send and receive audio i/o data bewteeen client and server

# HTTP → prompts
# HTTP streaming → AI responses
# WebSocket → audio

#library imports
import asyncio
import subprocess


#class imports
from voiceIn import Audio
from client import WSClient
import time


audio = Audio()
# wsclient = WSClient("ws://127.0.0.1:8000/ws/mochi")
wsclient = WSClient("wss://note-d1.tail8b0d7e.ts.net/ws/mochi")

#start tailscale before running program
#tailscale up in terminal
subprocess.run("tailscale up")


cloudClient = WSClient("")

async def run_mochigo():

    #making connection
    await wsclient.connect()

    while 1:
        #wait for wake() function to return true
        await asyncio.to_thread(audio.wake)


        #recieve audio file from voiceIn.py
        try:
            voiceInput = await asyncio.to_thread(audio.record)
        except:
            print("Could not recieve audio input, restarting loop")
            continue


        #send audio file to server 
        await wsclient.send(voiceInput)
        print("sent")


        #recieve audio output from server and save it 
        audioOut = await wsclient.recv()
        print(f"Output message: {audioOut}")


        #play the audio output file 


        #network flush 
        await asyncio.sleep(0.01)



if __name__ == "__main__":
    try:
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
