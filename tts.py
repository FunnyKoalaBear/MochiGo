import requests
import pygame
import os

API_KEY = "sk_9deab077f77ba93dd31e186d82fac8016ecbb0f801a63d98" 
VOICE_ID = "EXAVITQu4vr4xnSDxMaL" 

text_to_say = "Hi this is your favourite mochi"
output_file = "api_speech.mp3"

def generate_and_play():
    print("Connecting to ElevenLabs API directly...")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    
    data = {
        "text": text_to_say,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    # 3. Send the payload and download the MP3
    response = requests.post(url, json=data, headers=headers)
    
    # 4. Check if it succeeded (Status Code 200 means OK)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
            
        print("Playing audio...")
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.quit()
        
        if os.path.exists(output_file):
            os.remove(output_file)
    else:
        # If it fails, print the exact error from ElevenLabs
        print(f"API Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    generate_and_play()