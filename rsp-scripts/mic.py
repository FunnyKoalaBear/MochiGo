import sounddevice as sd
from scipy.io.wavfile import write


#mic functionality
class Microphone():

    def __init__(self):

        #basic configuration 
        self.sample_rate = 44100
        self.channels = 1
        self.duration = 5

        sd.default.samplerate = self.sample_rate
        sd.default.channels = self.channels

    def record(self):
        print("Starting recording")
        self.myrecording = myrecording = sd.rec(int(self.duration * self.sample_rate), dtype='int16')

        sd.wait() #pauses function till recording is complete

        #saving recording 
        filename = "micRecording.wav"
        write(filename, self.sample_rate, self.myrecording)
        print(f"💾 Saved successfully as '{filename}'.")


    def play(self):
        pass


#runs this if file is run directly 
if __name__ == "__main__":
    mic = Microphone()

    while True:
        mic.record()
        exit()