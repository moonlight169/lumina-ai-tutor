from src.tts_engine import TTSEngine

tts = TTSEngine()

print("TTS พร้อมใช้งาน (พิมพ์ exit เพื่อออก)")

while True:

    text = input("Text: ")

    if text.lower() == "exit":
        break

    tts.speak(text)