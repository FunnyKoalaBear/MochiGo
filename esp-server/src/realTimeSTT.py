import os, sys, json, pyaudio
from vosk import Model, KaldiRecognizer
import numpy as np # Used for fast volume calculation
import time

# --- Model configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(BASE_DIR, ".."))

MODEL_DIR = os.path.join(ROOT_DIR, "models")

#ENGLISH MODELS
#MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15")   #vosk-model tiny
#MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-en-us-0.22-lgraph/vosk-model-en-us-0.22-lgraph")   #vosk-model medium
MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-en-us-0.22/vosk-model-en-us-0.22")   #vosk-model large

#JAPANESE MODELS
#MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-small-ja-0.22/vosk-model-small-ja-0.22")   #Japanese vosk model small
#MODEL_PATH = os.path.join(MODEL_DIR, "vosk-model-ja-0.22/vosk-model-ja-0.22")   #Japanese vosk-model large

# --- Model check ---
if not os.path.exists(MODEL_PATH):
    print(f"❌ Error: Model folder '{MODEL_PATH}' not found.")
    sys.exit(1)


# --- Starting model and microphone stream ---
print("Loading model...")
model = Model(MODEL_PATH) #loading model
rec = KaldiRecognizer(model, 16000) #160000hz audio input

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()


# --- SILENCE SENSITIVITY --
SILENCE_TIMEOUT = 0.6 #seconds
SILENCE_THRESHOLD = np.mean([np.abs(np.frombuffer(stream.read(1024), dtype=np.int16)).mean() for _ in range(50)]) * 1.5 #Below threshold indicates silence, 50-200 for good mics, 500+ for noisy mics


# --- LATENCY VARIABLES ---
last_partial_time = 0
current_text = ""
speaking = False


# --- PROCESS LIVE AUDIO ---
print("🎧 Listening... ")

try:
    while True:
        # Read data from the microphone
        data = stream.read(1024, exception_on_overflow=False)
        
        #MANUAL SILENCE CHECK TO STOP EARLY 
        audio_chunk = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_chunk).mean()

        if (volume < SILENCE_THRESHOLD * 1.2):

            #dynamically updating the silence threshold if the room got quieter 
            SILENCE_THRESHOLD = (SILENCE_THRESHOLD * 0.95) + (volume * 1.5 * 0.05) 
            #print(f"Silence threshold updated to {SILENCE_THRESHOLD}")

        # Feed data to Vosk (Non-Blocking)
        if rec.AcceptWaveform(data):
            # A full sentence/phrase was completed (Silence reached)
            processing_finish_time = time.perf_counter()
            result = json.loads(rec.Result())

            if result['text']:
                print(f"📝 Final output: {result['text']}")
                current_text = ""
                speaking = False

                latency = processing_finish_time - last_partial_time
                is_speaking = False
                print(f"⏱️  Latency: {latency:.4f} seconds (Silence detected -> Output)")

        else:
            # --- PARTIAL RESULT (User is speaking) ---
            partial = json.loads(rec.PartialResult())
            
            # If the partial result contains text, it means you are currently talking.
            # We update the timestamp to "now".
            if partial['partial'] != "":
                last_partial_time = time.perf_counter()

                current_text = partial['partial']

                # --- 1. CALCULATE VOLUME FIRST ---
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_chunk).mean()
                #print(f"Current volume is {volume}")            


                # If volume is loud, update the timer (User is physically making noise)
                if volume > SILENCE_THRESHOLD:
                    last_speech_time = time.perf_counter()
                    # print(volume)
                    speaking = True
    
                # Print current thought
                print(f"🗣️  ... {current_text}", end='\r')
                            


        # If we are currently "speaking" but the volume is low...
        if speaking and (volume < SILENCE_THRESHOLD):
            # Check how long it has been quiet
            time_since_speech = time.perf_counter() - last_speech_time
            
            if time_since_speech > SILENCE_TIMEOUT:
                # 🛑 FORCE STOP! The user stopped talking 0.5s ago.
                print(f"\n⚡ Force Final: {current_text}")
                
                # Reset for next sentence
                rec.Reset()
                speaking = False
                current_text = ""



except KeyboardInterrupt:
    print("\n🛑 Stopping...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()