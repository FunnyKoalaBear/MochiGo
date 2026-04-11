import time
import signal
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

# --- Setup ---
# 400kHz baudrate for smoother animations
serial = i2c(port=1, address=0x3C)
display = ssd1306(serial)


class Eyes:
    # [x1, y1, x2, y2]
    NEUTRAL = [40, 10, 80, 60]

    def __init__(self, display):
        self.display = display
        self.display.clear()


    def neutral(self):
        with canvas(self.display) as draw:
            draw.ellipse(self.NEUTRAL, outline="white", fill="white")


    def look_around(self):
        #Moves the eyes right, then left, then back to center.

        # Look Right
        for i in range(0, 31, 3):
            with canvas(self.display) as draw:
                coords = [self.NEUTRAL[0] + i, self.NEUTRAL[1],
                          self.NEUTRAL[2] + i, self.NEUTRAL[3]]
                draw.ellipse(coords, outline="white", fill="white")

        # Look Left
        for i in range(30, -31, -3):
            with canvas(self.display) as draw:
                coords = [self.NEUTRAL[0] + i, self.NEUTRAL[1],
                          self.NEUTRAL[2] + i, self.NEUTRAL[3]]
                draw.ellipse(coords, outline="white", fill="white")

        # Back to Center
        for i in range(-30, 1, 3):
            with canvas(self.display) as draw:
                coords = [self.NEUTRAL[0] + i, self.NEUTRAL[1],
                          self.NEUTRAL[2] + i, self.NEUTRAL[3]]
                draw.ellipse(coords, outline="white", fill="white")


    def happy(self):
        with canvas(self.display) as draw:
            # Drawing two triangles to create 'joyful' eyes
            draw.polygon([(30, 50), (64, 10), (98, 50)], outline="white", fill="white")
            draw.polygon([(35, 50), (64, 15), (93, 50)], outline="black", fill="black")


# SCRAPPED FOR NOW CINCE IT LOOKS WEIRD
#    def sleepy(self):
#        with canvas(self.display) as draw:
#            draw.rectangle((40, 45, 88, 55), outline="white", fill="white")


    def blink(self):
        #Animates a single blink by moving the top lid down and bottom lid up
        x1, y1, x2, y2 = self.NEUTRAL

        # Closing
        while y1 < y2 - 10:
            y1 += 5
            y2 -= 2
            with canvas(self.display) as draw:
                draw.ellipse([x1, y1, x2, y2], outline="white", fill="white")

        # Opening
        while y1 > self.NEUTRAL[1]:
            y1 -= 5
            y2 += 2
            with canvas(self.display) as draw:
                draw.ellipse([x1, y1, x2, y2], outline="white", fill="white")



# --- Execution Logic ---
running = True

def handle_exit(sig, frame):
    global running
    print("\n[MochiGo] Shutting down eyes safely...")
    running = False


def main():
    my_eyes = Eyes(display)

    signal.signal(signal.SIGINT, handle_exit)

    print("Eyes active, going through different states. Press Ctrl+C to exit.")

    while running:
        # Simple behavior pattern Showcase
        my_eyes.neutral()
        time.sleep(2)

        my_eyes.blink()
        time.sleep(1)

        my_eyes.look_around()
        time.sleep(1)

        my_eyes.happy()
        time.sleep(1.5)

    # Final cleanup
    display.clear()
    print("Cleanup complete.")



if __name__ == "__main__":
    main()
