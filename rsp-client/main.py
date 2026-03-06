#this program needs to send and receive audio i/o data bewteeen client and server

# HTTP → prompts
# HTTP streaming → AI responses
# WebSocket → audio

#library imports


#class imports
from voiceIn import Audio
from client import sendQuery

audio = Audio()


#function definitions 
def recieveAudio():
    try:
        userSpeech = audio.record()
        return userSpeech
    except:
        print("Audio could not be recieved")
        exit()

def run_mochigo():

    while 1:

        #wait for wake() function to return true
        audio.wake()

        #recieve audio file from voiceIn.py
        try:
            voiceInput = audio.record()
        except:
            print("Could not recieve audio input, restarting loop")
            continue

        #send audio file to server 
        sendQuery()
    

        #recieve audio output from server and save it 


        #play audio output file 
    



if __name__ == "__main__":
    run_mochigo()



#Pipeline
#Wait for wake function
#Recieve audio file from voiceIn.py
#Send audio input to server 
#Recieve audio output from server
#Make voiceOut.py play audio output on speakers  
