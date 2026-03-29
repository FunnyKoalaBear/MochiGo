#this code is for the eyes of the robot
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import time
import signal

serial = i2c(port=1, address=0x3C)

# SSD1306->128x64 OLED, SSD1316->128x32 OLED
display = ssd1306(serial)


class Eyes():

    def __init__(self, display):
        self.display = display
        self.display.clear()


    def neutral(self):

        with canvas(display) as draw:
            draw.ellipse((40, 10, 80, 60), outline="white", fill="white")

    #looks right and left (neutral eyes)
    def look_around(self):

        for i in range(0, 40, 3):
            with canvas(display) as draw:
                draw.ellipse((44+i, 10, 84+i, 60), outline="white", fill="white")

        for i in range(40, -41, -3):
            with canvas(self.display) as draw:
                draw.ellipse((44 + i, 10, 84 + i, 60), outline="white", fill="white")

        for i in range(-40, 1, 3):
            with canvas(self.display) as draw:
                draw.ellipse((44 + i, 10, 84 + i, 60), outline="white", fill="white")

    def happy(self):
        with canvas(self.display) as draw:
            # (Bottom-Left), (Top-Middle), (Bottom-Right)
            draw.polygon([(30, 50), (64, 10), (98, 50)], outline="white", fill="white")
            draw.polygon([(35, 50), (64, 15), (93, 50)], outline="black", fill="black")

    def sleepy(self):

        with canvas(display) as draw:
            draw.rectangle((40, 45, 88, 55), outline="white", fill="white")

    def blink(self):
        pass



def handle_exit(sig, frame):
        global running
        print("\n[MochiGo] Shutting down eyes safely...")
        running = False



def main():

    my_eyes = Eyes(display)

    running = True

    # Intercept CTRL+C and route it to our handle_exit function
    signal.signal(signal.signal.SIGINT, handle_exit)

    print("Eyes active. Press Ctrl+C to exit.")

    while running:
        my_eyes.neutral()
        time.sleep(0.1) 

    # This only runs once 'running' becomes False
    display.cleanup()
    print("Cleanup complete.")



if __name__ == '__main__':
    main()
