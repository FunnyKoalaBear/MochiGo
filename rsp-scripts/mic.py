import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class Microphone():
    def __init__(self):
        self.sample_rate = 48000
        self.channels = 2  # Stereo to capture the hardware accurately
        self.duration = 5

    def record(self):
        print("🎤 Recording... Speak normally!")
        
        # 1. Record directly into float32 space (decimals between -1.0 and 1.0)
        raw_recording = sd.rec(int(self.duration * self.sample_rate), 
                               samplerate=self.sample_rate,
                               channels=self.channels, 
                               dtype='float32')
        sd.wait()

        # 2. Extract ONLY the Left Channel
        left_channel = raw_recording[:, 0]

        # 3. Apply the gain (multiply the decimals)
        gain_multiplier = 15.0  # Safe to push this high in float space
        boosted_audio = left_channel * gain_multiplier

        # 4. Clip strictly at -1.0 and 1.0 so it is physically impossible to buzz or crackle
        boosted_audio = np.clip(boosted_audio, -1.0, 1.0)

        # 5. Convert smoothly back to standard 16-bit integers for the final WAV file
        # We multiply by 32767 to map the 1.0 decimal to the top of the 16-bit ceiling
        final_audio = np.int16(boosted_audio * 32767)

        # 6. Save the file
        filename = "new.wav"
        write(filename, self.sample_rate, final_audio)
        print(f"💾 Saved crystal-clear file as '{filename}'.")

if __name__ == "__main__":
    mic = Microphone()
    mic.record()