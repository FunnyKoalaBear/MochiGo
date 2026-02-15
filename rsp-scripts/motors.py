# this program will control the motors for cam and follower mechanism of the project 

#libraries
import time
import pigpio

class Motor():

    def __init__(self):
        self.pi = pigpio.pi() #using gpio pins
        self.pi.set_mode(12, pigpio.OUTPUT) #setting pin 32 to output
        self.pi.set_pad_strength(2, 14) #2-14mA current draw range
        self.pi.set_servo_pulsewidth(12, 1500) #sets servo to middle position 


    def oscillate(self, delay, step):
        #clockwise 
        for i in range(2500, 500, -step):
            self.pi.set_servo_pulsewidth(12, i)
            time.sleep(delay)


        time.sleep(0.5)

        #anticlockwise  
        for i in range(500, 2500, step):
            self.pi.set_servo_pulsewidth(12, i)
            time.sleep(delay)

        time.sleep(0.5)        
    
    def stop(self):
        self.pi.set_servo_pulsewidth(12, 0)


m = Motor()


# while True:
#     m.oscillate(0.01, 10)


try:
    while True:
        m.oscillate(0.01, 10)
except KeyboardInterrupt:
    m.stop()    