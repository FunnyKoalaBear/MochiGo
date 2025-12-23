import os, sys, json, pyaudio
from vosk import Model, KaldiRecognizer
import numpy as np # Used for fast volume calculation
import time
import webrtcvad

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


# --- Starting model ---
print("Loading model...")
model = Model(MODEL_PATH) #loading model
rec = KaldiRecognizer(model, 16000) #160000hz audio input

# --- Initialize VAD ---
# Mode 0 is least aggressive, 3 is most aggressive (filters most noise)
vad = webrtcvad.Vad(3) 
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 30 # ms
# Calculate frame size: 16000 * 0.03 = 480
CHUNK_SIZE = int(SAMPLE_RATE * (CHUNK_DURATION_MS / 1000.0))


# --- Starting microphone stream ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=CHUNK_SIZE)
stream.start_stream()


# --- SILENCE SENSITIVITY --
SILENCE_TIMEOUT = 0.6 #seconds

#Below threshold indicates silence, 50-200 for good mics, 500+ for noisy mics
SILENCE_THRESHOLD = np.mean([np.abs(np.frombuffer(stream.read(1024), dtype=np.int16)).mean() for _ in range(50)]) * 1.5 


# --- LATENCY VARIABLES ---
last_partial_time = last_speech_time = time.perf_counter() #CREATES 2 VARIABLES YUHHh
current_text = ""
speaking = False


# --- PROCESS LIVE AUDIO ---
print("🎧 Listening... ")

try:
    while True:
        # Read data from the microphone and initialize time
        last_partial_time = time.perf_counter()
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        
        #Ensuring length of chunk is 960 bytes, for 480 samples (2 bytes each)
        expected_bytes = CHUNK_SIZE * 2
        if len(data) < expected_bytes:
            # Pad with zeros (silence) if the buffer came up short
            data = data.ljust(expected_bytes, b'\x00')
        elif len(data) > expected_bytes:
            # Truncate if expected bytes is too long
            data = data[:expected_bytes]

        # WE COULD ALSO DO 
        # if len(data) != expected_bytes: continue

        #Variables for dynamic audio changing
        audio_chunk = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(audio_chunk).mean()

        # VAD CHECK
        try:
            is_speech = vad.is_speech(data, SAMPLE_RATE)
            #if is_speech: print("Yes")
            #else: print("no")
        except webrtcvad.Error:
            is_speech = False
            print(webrtcvad.Error)
        
        is_active = is_speech or (volume > SILENCE_THRESHOLD)
        #print(is_active)

        #updating silence threshold 
        if ((volume < SILENCE_THRESHOLD * 1.2) & (not is_active and not speaking)):
            #dynamically updating the silence threshold if the room got quieter 
            SILENCE_THRESHOLD = (SILENCE_THRESHOLD * 0.95) + (volume * 1.5 * 0.05) 
            #print(f"Silence threshold updated to {SILENCE_THRESHOLD}")

        # Feed data to Vosk (Non-Blocking) IF speech is detected
        if is_active or speaking:
            if rec.AcceptWaveform(data):
                # A full sentence/phrase was completed (Silence reached)
                result = json.loads(rec.Result())

                if result['text']:
                    print(f"📝 Final output: {result['text']}")
                    current_text = ""
                    speaking = False

                    #latency = processing_finish_time - last_partial_time
                    latency = time.perf_counter() - last_speech_time #new latency code 
                    is_speaking = False
                    print(f"⏱️  Latency: {latency:.4f} seconds")
            else:
                # --- PARTIAL RESULT (User is speaking) ---
                #print("Entering this")
                partial = json.loads(rec.PartialResult())
                
                # If the partial result contains text, it means you are currently talking.
                # We update the timestamp to "now".
                if partial['partial'] != "":
                    last_partial_time = time.perf_counter()

                    current_text = partial['partial']

                    # --- 1. CALCULATE VOLUME FIRST ---
                    audio_chunk = np.frombuffer(data, dtype=np.int16)
                    #volume = np.abs(audio_chunk).mean()
                    #print(f"Current volume is {volume}")        
                    
                    # If volume is loud, update the timer (User is physically making noise)
                    if volume > SILENCE_THRESHOLD:
                        last_speech_time = time.perf_counter()
                        # print(volume)
                        speaking = True
        
                    # Print current thought
                    print(f"🗣️  ... {current_text}", end='\r')
                            


        # If we are currently "speaking" but the volume is low...
        if speaking and not is_active:
            # Check how long it has been quiet
            time_since_speech = time.perf_counter() - last_speech_time
            #print(time_since_speech)
            if time_since_speech > SILENCE_TIMEOUT :
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