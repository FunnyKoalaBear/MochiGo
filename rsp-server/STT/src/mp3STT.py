#this program performs SST on a single audio file 
import wave
import json
import sys
import os
from vosk import Model, KaldiRecognizer

import time

def load():
    # --- STT MODEL CONFIGURATION ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
    ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, ".."))

    MODEL_DIR = os.path.join(ROOT_DIR, "models")
    #MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15")   #vosk-model tiny
    #MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-en-us-0.22-lgraph/vosk-model-en-us-0.22-lgraph")   #vosk-model medium
    MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-en-us-0.22/vosk-model-en-us-0.22")   #vosk-model large

    #MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-small-ja-0.22/vosk-model-small-ja-0.22")   #Japanese vosk model small
    #MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-ja-0.22/vosk-model-ja-0.22")   #Japanese vosk-model large

    #converts .mp3 file to .wav
    #ffmpeg -i original_recording.mp3 -acodec pcm_s16le -ar 16000 -ac 1 test_audio.wav
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    AUDIO_FILE = os.path.join(DATA_DIR, "sampleRecording.wav")

    # --- CHECKS ---
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: Model folder '{MODEL_PATH}' not found.")
        sys.exit(1)

    if not os.path.exists(AUDIO_FILE):
        print(f"❌ Error: Audio file '{AUDIO_FILE}' not found.")
        sys.exit(1)

        
    # --- SETUP ---
    print(f"Loading Model...")
    model = Model(MODEL_PATH)

    return model


def call(AUDIO_FILE, model):
    # Open audio file
    wf = wave.open(AUDIO_FILE, "rb")

    # check file properties
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("❌ Error: Audio file must be WAV format mono PCM.")
        sys.exit(1)

    # Initialize Recognizer with file's sample rate
    rec = KaldiRecognizer(model, wf.getframerate())

    print(f"🎧 Processing '{AUDIO_FILE}'...")

    # --- PROCESS FILE ---
    start = time.perf_counter()

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print(f"📝 Text: {result['text']}")

    # Process remaining buffer
    final_result = json.loads(rec.FinalResult())
    if final_result['text']:
        print(f"📝 Text: {final_result['text']}")


    end = time.perf_counter()
    print(f"Time taken: {end - start:.6f} seconds")
    wf.close()

    return final_result['text']



if __name__ == "__main__":
    file = "rsp-server\STT\data\sampleRecording.wav"
    model = load()
    call(file, model)


