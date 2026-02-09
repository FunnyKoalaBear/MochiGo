# this program will control eye movement of the mochigo
# OLED chip name SSD1306 (I2C)
#library docmentation link https://luma-oled.readthedocs.io/en/latest/api-documentation.html#luma.oled.device.ssd1306.capabilities

from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw
import sys

serial = i2c(port=1, address=0x3C)
width= 128 
height= 32
display = ssd1306(serial, width=width, height=height)


#eye functionality
class Eyes():
    
    def __init__(self, display):
        self.display = display 
        self.display.clear() #erase everything at start 
        self.display.bounding_box = (0, 0, width-1, height-1)

        #images for expressions
        Image.open("img/neutral.png") #neutral expression
 
    def neutral(self):
        with canvas(self.display) as draw:
            
            #making background whtie
            draw.rectangle(self.display.bounding_box, outline="white", fill="white")
            
            #the eyes 
            #draw.text((10, 20), "Hello World", fill="black")
            with Image.open("img/neutral.png") as im:
                draw = ImageDraw.Draw(im)
                im.save(sys.stdout, "PNG")
            


    def blink(self):
        pass


#eye logic 
eyes = Eyes(display)

while True:
    eyes.neutral()
    #time.sleep(0.5)

    #add time out functionality to power down with cleanup()