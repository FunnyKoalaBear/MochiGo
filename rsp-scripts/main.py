from eyes import Eyes, display
from motors import Motor
import time

eyes = Eyes(display)
motors = Motor()

#logic comes here 
while True:
    motors.oscillate(0.01, 10)
    eyes.neutral()

    #time.sleep(0.5)       
