import wave
import json
import sys
import os
from vosk import Model, KaldiRecognizer

# --- CONFIGURATION ---
MODEL_PATH = "model"
AUDIO_FILE = "test_audio.wav"
TARGET_PHRASE = "hello world how are you" # 👈 CHANGE THIS to match your audio

# --- SETUP ---
if not os.path.exists(MODEL_PATH) or not os.path.exists(AUDIO_FILE):
    print("❌ Error: Missing model or audio file.")
    sys.exit(1)

model = Model(MODEL_PATH)
wf = wave.open(AUDIO_FILE, "rb")

# Check sample rate matches (Vosk usually needs 16000, but adapts if you tell it)
if wf.getnchannels() != 1:
    print("❌ Error: Audio must be Mono (1 channel).")
    sys.exit(1)

rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True) # IMPORTANT: Enables word-by-word timestamp & confidence

print(f"👨‍🏫 Grading pronunciation against target: '{TARGET_PHRASE}'")

# --- PROCESS FILE ---
results = []
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        part = json.loads(rec.Result())
        if 'result' in part:
            results.extend(part['result'])

# Get final bits
part = json.loads(rec.FinalResult())
if 'result' in part:
    results.extend(part['result'])

wf.close()

# --- SCORING LOGIC ---
print("\n--- 📊 PRONUNCIATION REPORT ---")

detected_words = [r['word'] for r in results]
target_words = TARGET_PHRASE.lower().split()
full_sentence_detected = " ".join(detected_words)

print(f"🗣️  You said: '{full_sentence_detected}'")

if not results:
    print("❌ No speech detected.")
    sys.exit(0)

# Compare word by word
score_sum = 0
matched_count = 0

for i, word_obj in enumerate(results):
    word = word_obj['word']
    conf = word_obj['conf']
    
    # Simple check: Is this word in our target list?
    if word in target_words:
        status = ""
        if conf > 0.90:
            status = "✅ Excellent"
        elif conf > 0.75:
            status = "⚠️  Good"
        else:
            status = "❌ Unclear/Mumbled"
        
        print(f"   Word: '{word.ljust(12)}' | Confidence: {int(conf*100)}% | {status}")
        score_sum += conf
        matched_count += 1
    else:
        print(f"   Word: '{word.ljust(12)}' | (Not in target phrase)")

# Final Score Calculation
if matched_count > 0:
    avg_score = (score_sum / len(target_words)) * 100
    print(f"\n🏆 Overall Pronunciation Score: {int(avg_score)}/100")
else:
    print("\n🏆 Overall Score: 0/100 (Words did not match target)")