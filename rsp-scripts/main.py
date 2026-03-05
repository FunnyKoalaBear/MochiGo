from eyes import Eyes, display
from omniMic import Microphone 
import time
import threading 

try:
    from motors import Motor 
except:
    #import this if program is running on Rsp5
    from motors5 import Motor

#initialising classes 
eyes = Eyes(display)
motors = Motor()
mic = Microphone()


#setting up functions 
def neutral():
    while not killSwitch.is_set():
            try:
                eyes.neutral()
            except Exception:
                break # Exit silently if the main program is shutting down

def oscillate(delay, step):
    while not killSwitch.is_set():
            try:
                motors.oscillate(delay, step)
            except Exception:
                break

def record():
    while not killSwitch.is_set():
            try:
                mic.record()
            except Exception:
                break


#starting threads 
threads = []
t1 = threading.Thread(target=neutral, daemon=True)
threads.append(t1)

t2 = threading.Thread(target=oscillate, kwargs={"delay":0.01, "step":10}, daemon=True)
threads.append(t2)

t3 = threading.Thread(target=record, daemon=True)
threads.append(t3)

killSwitch = threading.Event() #daemon event that toggles all functions to stop 


#starting all background actions 
for t in threads:
    t.start()


#mochigo logic
try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    killSwitch.set()

    #time for threads to finish their current actions cleanly and prevent error
    for t in threads:
        t.join(timeout=0.5)
    
    motors.stop()
    
    print("\nShutting down Mochigo...")
    exit()
    