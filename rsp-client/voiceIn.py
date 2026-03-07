#This program will run a basic VAD on the raspberry to check if the user is speaking
#If the user is speaking this will trigger rsp-scripts to start mic.py in the scripts
#The output of mic.py will be taken and sent to the main.py 

class Audio():
    def __init__(self):
        self.audioFile = "audio.mp4"
        self.text = "hi how are you doing today"

    def wake(self):
        #continuous function that checks if user is talking 
        
        #simulating it by waiting for input 
        start = input("Press enter to start talking")
        print("Wake triggered!")


    def record(self):
        #calls mic.py to record from rsp-script
        #sends recorded file to main.py 
        self.text = input("Enter your query: ")
        return self.text