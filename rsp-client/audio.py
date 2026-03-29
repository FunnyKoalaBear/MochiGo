#this program will be used to convert live recording to mp3 sound and then play it back live through the device speakers
import sounddevice as sd
import soundfile as sf
import miniaudio as ma 
import time
import numpy as np 
from pydub import AudioSegment
import asyncio
import wave 
fileMp3 = "rsp-client/Audio_Output/tts_out.mp3"
fileWav = "rsp-client/Audio_Output/tts_in.wav"
#configuration

import miniaudio

#function to record audio
async def recordMp3(filename, fs=44100):
    recorded_chunks = []

    # 1. Define a callback to grab audio data as it arrives
    def callback(indata, frames, time, status):
        if status:
            print(f"Audio Status Warning: {status}") # Helps debug buffer overruns
        recorded_chunks.append(indata.copy())

    await asyncio.to_thread(input, "Press Enter to START recording...")

    # 2. Start the stream - EXPLICITLY set dtype to float32
    with sd.InputStream(samplerate=fs, channels=1, dtype='float32', callback=callback):
        await asyncio.to_thread(input, "RECORDING... Press Enter to STOP.")

    # 3. Process the recorded data
    if not recorded_chunks:
        print("No audio recorded.")
        return

    print("Converting to MP3...")
    
    # Flatten the list of chunks into one long NumPy array
    full_recording = np.concatenate(recorded_chunks, axis=0)
    
    # FIX: Clip the values strictly between -1.0 and 1.0 to prevent integer overflow
    full_recording = np.clip(full_recording, -1.0, 1.0)
    
    # Convert float32 to int16 for MP3 compatibility safely
    audio_int16 = (full_recording * 32767).astype(np.int16)

    # 4. Create Pydub segment and export
    audio_segment = AudioSegment(
        audio_int16.tobytes(), 
        frame_rate=fs,
        sample_width=audio_int16.dtype.itemsize, 
        channels=1
    )

    audio_segment.export(filename, format="mp3", bitrate="192k")
    print(f"Saved: {filename}")



def recordWav(filename, fs=44100):
    recorded_chunks = []

    # 1. Define a callback to grab audio data as it arrives
    def callback(indata, frames, time, status):
        if status:
            print(f"Audio Status Warning: {status}") # Helps debug buffer overruns
        recorded_chunks.append(indata.copy())

    input("Press Enter to START recording...")

    # 2. Start the stream - EXPLICITLY set dtype to float32
    with sd.InputStream(samplerate=fs, channels=1, dtype='float32', callback=callback):
        input("RECORDING... Press Enter to STOP.")

    # 3. Process the recorded data
    if not recorded_chunks:
        print("No audio recorded.")
        return

    print("Saving to WAV...")
    
    # Flatten the list of chunks into one long NumPy array
    full_recording = np.concatenate(recorded_chunks, axis=0)
    
    # FIX: Clip the values strictly between -1.0 and 1.0 to prevent integer overflow
    full_recording = np.clip(full_recording, -1.0, 1.0)
    
    # Convert float32 to int16 for MP3 compatibility safely
    audio_int16 = (full_recording * 32767).astype(np.int16)

    # 4. Save using the built-in wave library
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)           # Mono
        wf.setsampwidth(2)           # 2 bytes = 16-bit PCM
        wf.setframerate(fs)          # Sample rate (16000)
        wf.writeframes(audio_int16.tobytes())

    print(f"Saved: {filename}") 



#function to playback audio
async def playback(file):
    
    #decode mp3 file    
    audioFile = miniaudio.decode_file(file)
    channels = audioFile.nchannels
    audioFile.samples = np.array(audioFile.samples)

    if channels > 1:
        audioFile.samples = audioFile.samples.reshape(-1, channels)
    #play decoded audio 

    
    sd.play(audioFile.samples, audioFile.sample_rate)
    sd.wait()


#record()
# recordWav(fileWav)
# time.sleep(2)
# playback(fileMp3)