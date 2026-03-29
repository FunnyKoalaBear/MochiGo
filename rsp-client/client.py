#this program needs to send and receive audio i/o data bewteeen client and server

# HTTP → prompts
# HTTP streaming → AI responses
# WebSocket → audio

#library imports
import asyncio
import subprocess


#class imports
from voiceIn import Audio
from clientDetails import WSClient
import time
from audio import recordWav, playback


audio = Audio()
# wsclient = WSClient("ws://127.0.0.1:8000/ws/mochi")
wsclient = WSClient("ws://note-d1.tail8b0d7e.ts.net:8000/ws/mochi")

#start tailscale before running program
#tailscale up in terminal
subprocess.run(["tailscale", "up"])


cloudClient = WSClient("")
wavFile = "Audio_Output/tts_in.wav"
mp3File = "Audio_Output/tts_out.mp3"


async def run_mochigo():

    #making connection
    await wsclient.connect()

    while 1:
        #This is done by running running local vosk model
        #wait for wake() function to return true
        #await asyncio.to_thread(audio.wake)

        #text input
        #recieve audio file from voiceIn.py
        # try:
        #     voiceInput = await asyncio.to_thread(audio.record)
        # except:
        #     print("Could not recieve audio input, restarting loop")
        #     continue
        
        #record user input
        await recordWav(wavFile)

        #send user voice to server for TTS
        with open(wavFile, "rb") as f:
            wav_bytes = f.read()

        #send audio file to server for SST -> LLM -> TTS
        await wsclient.send(wav_bytes)
        print("sent")


        #recieve audio output from server and build it as an mp3 file
        await wsclient.recvAudio()

        #play the audio output file
        #await asyncio.to_thread(playback, mp3File)

	#play the audio file through BlueTooth
	############################################################################
        print("Playing file though connected bluetooth device")
        process = await asyncio.create_subprocess_exec("paplay", mp3File)
        await process.wait()
	############################################################################

        #network flush and loopback 
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
