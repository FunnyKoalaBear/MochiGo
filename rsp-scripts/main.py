from eyes import Eyes, display
from motors import Motor

eyes = Eyes(display)
motors = Motor()

#logic comes here 
while True:
    motors.oscillate()
    eyes.neutral()

    #time.sleep(0.5)    