from eyes import Eyes, display
from motors import Motor 
from omniMic import Microphone 
import time
import threading 

#initialising classes 
eyes = Eyes(display)
motors = Motor()
mic = Microphone()


#mochigo logic

try:
    while True:
        motors.oscillate(0.01, 10)
        mic.record()
        eyes.neutral()
        time.sleep(10)

        #time.sleep(0.5)       

except KeyboardInterrupt:
    motors.stop() 



