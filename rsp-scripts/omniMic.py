#This program will be used to program the functionality of the INMP441  omnidirection microphone module 
#need to configure i2s to support audio input from GPIO pins first for the micrphone 
#add these lines to the file from sudo nano /boot/firmware/config.txt
# dtparam=i2s=on
# dtoverlay=googlevoicehat-soundcard

#run these to install needed libraries 
#sudo apt install libopenblas0
#sudo apt install libportaudio2 portaudio19-dev
#pip install sounddevice scipy (inside venv)

import sounddevice as sd
from scipy.io.wavfile import write


#mic functionality
class Microphone():

    def __init__(self):

        #basic configuration 
        self.sample_rate = 44100
        self.channels = 1
        self.duration = 5
    
    def record(self):
        pass

    def play(self):
        pass
    

#runs this if file is run directly 
if __name__ == "__main__":
    mic = Microphone()

    while True:
        pass


#to start a python webserver 
#python -m http.server 8000
# connect to it from local browser at http://192.168.1.190:8000