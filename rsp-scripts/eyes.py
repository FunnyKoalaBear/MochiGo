# this program will control eye movement of the mochigo
# OLED chip name SSD1306 (I2C)
#library docmentation link https://luma-oled.readthedocs.io/en/latest/api-d>

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw
import sys
import time

serial = i2c(port=1, address=0x3C)
width= 128
height= 32
display = ssd1306(serial, width=width, height=height)


#eye functionality
class Eyes():

    def __init__(self, display):
        self.display = display
        self.display.clear() #erase everything at start
        
        # self.pi.set_pad_strength(0, 16) #equalizing eye brightness

        self.display.bounding_box = (0, 0, width-1, height-1)

        #images for expressions
        neutralR = Image.open("img/neutral.png")
        neutralR = neutralR.crop([6, 0, 56, 32])
        self.neutral_img = neutralR.resize((width, height)).convert("1") #1>

    

    def neutral(self):
        # with canvas(self.display) as draw:

            #making background whtie
        #draw.rectangle(self.display.bounding_box, outline="white", fill="w>

            #the eyes
            #draw.text((10, 20), "Hello World", fill="black")

            # with Image.open("img/neutral.png") as im:
            #     draw = ImageDraw.Draw(im)
            #     im.save(sys.stdout, "PNG")

            # image = Image.open("img/neutral.png", (width, height))
            # draw = ImageDraw.Draw(image)
        self.display.display(self.neutral_img)



    def blink(self):
        pass

#add time out functionality to power down with cleanup()


#runs this if file is run directly 
if __name__ == "__main__":
    eyes = Eyes(display)

    while True:
        eyes.neutral()
        time.sleep(0.5)


