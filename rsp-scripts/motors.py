# this program will control the motors for cam and follower mechanism of the project 

#To make the pigpio library use PWM clock do the following:  
#temporary fix in terminal: 
#sudo killall pigpiod
#sudo pigpiod -t 0

#permanent fix in terminal 
#sudo nano /lib/systemd/system/pigpiod.service
#Modify the ExecStart line by adding -t 0
#ExecStart=/usr/bin/pigpiod -l -t 0
#sudo systemctl daemon-reload
#sudo systemctl restart pigpiod

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


if __name__ == "__main__":
    m = Motor()
    
    try:
        while True:
            m.oscillate(0.01, 10)
    except KeyboardInterrupt:
        m.stop()
