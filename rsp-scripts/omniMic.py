#This program will be used to program the functionality of the INMP441  omnidirection microphone module 

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write


class Microphone():

    def __init__(self):
        # 48kHz prevents Pi clock jitter, Stereo prevents channel crushing
        self.sample_rate = 48000 
        self.channels = 2
        self.duration = 5

        sd.default.samplerate = self.sample_rate
        sd.default.channels = self.channels
    
    def record(self):
        print("Starting recording...")
        # Back to standard int16 so the Pi handles the bit-translation properly
        self.myrecording = sd.rec(int(self.duration * self.sample_rate), dtype='int16')
        
        sd.wait() # pauses function till recording is complete

        # Isolate the active channel (0 for Left, change to 1 if it's Right)
        audio_data = self.myrecording[:, 0].astype(np.float32)

        # 1. DELETE THE STARTUP POP
        # Calculate how many samples are in the first 0.5 seconds and slice them off
        ignore_samples = int(0.5 * self.sample_rate)
        clean_audio = audio_data[ignore_samples:]

        # 2. REMOVE DC OFFSET
        # Center the audio perfectly at zero
        clean_audio = clean_audio - np.mean(clean_audio)

        # 3. BOOST THE VOLUME
        max_amplitude = np.max(np.abs(clean_audio))
        print(f"DEBUG: Loudest sound captured (excluding pop) was: {max_amplitude}")

        if max_amplitude > 0:
            # Scale it to 95% of the max 16-bit volume (32767)
            safe_multiplier = (32767 * 0.95) / max_amplitude
            print(f"DEBUG: Multiplying volume by {safe_multiplier:.2f}x")
            
            boosted_audio = clean_audio * safe_multiplier
        else:
            boosted_audio = clean_audio

        # Clip it safely and convert back to int16 format for the WAV file
        final_recording = np.clip(boosted_audio, -32768, 32767).astype(np.int16)

        # Save recording 
        filename = "new.wav"
        write(filename, self.sample_rate, final_recording)
        print(f"💾 Saved successfully as '{filename}'.")
    

#runs this if file is run directly 
if __name__ == "__main__":
    mic = Microphone()

    while True:
        mic.record()
        exit()
