#script to control motors on the raspberry pi 5

from gpiozero import Servo
import time


class Motor():
    def __init__(self):
        # gpiozero takes pulse widths in seconds (500us = 0.0005s, 2500us = 0.0025s)
        # Using GPIO pin 12
        self.servo = Servo(12, min_pulse_width=0.0005, max_pulse_width=0.0025)
        
        # Automatically moves to the middle position (equivalent to 1500us)
        self.servo.mid() 

    def oscillate(self, delay, steps=100):
        # gpiozero uses a scale of -1.0 to 1.0. 
        # We step through fractions to create a smooth sweep.
        
        # Clockwise (1.0 down to -1.0)
        for i in range(steps, -steps - 1, -1):
            self.servo.value = i / steps
            time.sleep(delay)

        time.sleep(0.5)

        # Anticlockwise (-1.0 up to 1.0)
        for i in range(-steps, steps + 1, 1):
            self.servo.value = i / steps
            time.sleep(delay)

        time.sleep(0.5)
    
    def stop(self):
        # detatch() cuts the PWM signal entirely (equivalent to pulsewidth 0)
        self.servo.detach() 


if __name__ == "__main__":
    m = Motor()
    
    try:
        while True:
            # We use 100 steps and a tiny delay to keep the sweep smooth
            m.oscillate(0.01, steps=100)
    except KeyboardInterrupt:
        m.stop()