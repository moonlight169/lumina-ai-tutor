import asyncio
from tts_engine import TTSEngine
from stt_engine import stt

# สร้าง Instance ของ TTS ไว้ข้างนอก
tts = TTSEngine()

async def main():
    print("--- Lumina AI System พร้อมใช้งาน ---")
    print("(พูดคำว่า 'exit' เพื่อออกจากโปรแกรม)")

    while True:
        # ใช้ await ภายใน async function ได้แล้ว
        text = await stt()

        if not text:
            continue

        print(f"คุณพูดว่า: {text}")

        if "exit" in text.lower():
            print("ปิดโปรแกรม...")
            break

        # เรียกใช้ TTS (เช็กใน tts_engine ว่า speak เป็น async หรือเปล่า)
        # ถ้าเพื่อนเขียนเป็น async ให้ใส่ await tts.speak(text)
        tts.speak(text)

if __name__ == "__main__":
    try:
        # ใช้ asyncio.run เป็นตัวจุดระเบิดการทำงาน
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  