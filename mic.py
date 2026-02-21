import sounddevice as sd
from scipy.io.wavfile import write

# --- Configuration ---
sample_rate = 44100  # Standard audio sampling rate (Hz)
duration = 5         # Recording duration in seconds
channels = 1         # Set to 1 because we wired L/R to GND for Mono

print(f"🎤 Starting a {duration}-second recording...")
print("Speak into the microphone now!")

# --- Record Audio ---
# sd.rec starts the recording in the background
recording = sd.rec(int(duration * sample_rate), 
                   samplerate=sample_rate, 
                   channels=channels, 
                   dtype='int16') # int16 is standard for WAV files

# sd.wait() pauses the script until the recording is completely finished
sd.wait() 

print("✅ Recording finished! Saving file...")

# --- Save to File ---
filename = "first_test_recording.wav"
write(filename, sample_rate, recording)

print(f"💾 Saved successfully as '{filename}'.")