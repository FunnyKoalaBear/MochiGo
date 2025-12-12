import os
import sys
import json
import pyaudio
from vosk import Model, KaldiRecognizer

import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, ".."))

MODEL_DIR = os.path.join(ROOT_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15") 

# --- CHECKS ---
if not os.path.exists(MODEL_PATH):
    print(f"❌ Error: Model folder '{MODEL_PATH}' not found.")
    sys.exit(1)

# --- SETUP ---
print(f"Loading Model from {MODEL_PATH}...")
model = Model(MODEL_PATH)

# Initialize Recognizer
# 16000 Hz is standard for Vosk. We must set the mic to match this.
rec = KaldiRecognizer(model, 16000)

# --- MICROPHONE SETUP ---
p = pyaudio.PyAudio()

# Open the microphone stream
# format=paInt16 -> 16-bit PCM (Required by Vosk)
# channels=1 -> Mono (Required by Vosk)
# rate=16000 -> 16kHz sample rate
# input=True -> We are recording
# frames_per_buffer=8000 -> Buffer size (adjust if you get lag/choppiness)
stream = p.open(format=pyaudio.paInt16, 
                channels=1, 
                rate=16000, 
                input=True, 
                frames_per_buffer=8000)

stream.start_stream()

print("🎧 Listening... (Press Ctrl+C to stop)")

# --- PROCESS LIVE AUDIO ---
try:
    while True:
        # Read data from the microphone
        data = stream.read(4000, exception_on_overflow=False)
        start = time.perf_counter()

        # Feed to Vosk
        if rec.AcceptWaveform(data):
            # A full sentence/phrase was completed
            result = json.loads(rec.Result())

            if result['text']:
                print(f"📝 You said: {result['text']}")

                end = time.perf_counter()
                print(f"Time taken: {end - start:.6f} seconds")
        else:
            # (Optional) Print partial results to see it typing as you speak
            # partial = json.loads(rec.PartialResult())
            # print(f"    ... {partial['partial']}", end='\r')
            pass

except KeyboardInterrupt:
    print("\n🛑 Stopping...")

finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()