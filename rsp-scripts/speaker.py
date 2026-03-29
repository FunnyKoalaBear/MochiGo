#This script will be used to send sudio to the connected bluetooth speaker
import subprocess
import os


def play_wav(file_path):
    print(f"Playing {file_path}")

    try:
        # 'paplay' plays the file directly through the PulseAudio sound servers
        os.system(f"paplay {file_path}")
        print("Playback complete!")

    except subprocess.CalledProcessError:
        print(f"Error: Could not play '{file_path}'. Check if the file exists and is a valid .wav format.")
    except FileNotFoundError:
        print("Error: The 'paplay' command was not found on this system.")


play_wav("micRecording.wav")
