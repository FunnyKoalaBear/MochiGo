#Install this to remove crackling sounds
# sudo apt install -y wget
# pip3 install adafruit-python-shell
# wget https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/raw/main/i2samp.py
# sudo -E env PATH=$PATH python3 i2samp.py

#run this line in the terminal to see if the speaker is wires properly 
#speaker-test -D plughw:0,0 -t sine -f 440 -c 1
#Built in audio file that says "Front center"
#aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav

#This script will be used to control the single mono speaker of the mochigo
import subprocess

def play_wav(file_path):
    print(f"Sending audio data to amplifier... Playing {file_path}")

    try:
        # 'aplay' plays the file directly through the ALSA audio drivers
        subprocess.run(["aplay", file_path], check=True)
        print("Playback complete!")

    except subprocess.CalledProcessError:
        print(f"Error: Could not play '{file_path}'. Check if the file exists and is a valid .wav format.")
    except FileNotFoundError:
        print("Error: The 'aplay' command was not found on this system.")

# Replace 'mochigo_greeting.wav' with the path to your actual audio file
play_wav("first_test_recording.wav")
