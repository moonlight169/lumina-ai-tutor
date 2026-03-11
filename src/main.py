import asyncio
from tts_engine import TTSEngine
from stt_engine import stt
from vtube_bridge import lipsync, init_vts, close_vts

# สร้าง Instance ของ TTS
tts = TTSEngine()

async def main():
    # 1. เตรียมระบบ VTube Studio ให้พร้อมก่อนเริ่มลูป
    await init_vts()
    
    print("\n--- 🎓 Lumina AI Tutor พร้อมใช้งาน ---")
    print("(พูดเพื่อเริ่มสนทนา หรือพูด 'exit' เพื่อปิดโปรแกรม)")

    try:
        while True:
            # 2. รับเสียงจากไมโครโฟน (STT)
            text = await stt()

            if not text:
                continue

            print(f"🗣️ คุณ: {text}")

            if "exit" in text.lower():
                print("👋 กำลังปิดระบบ...")
                break

            # 3. สร้างไฟล์เสียงจากข้อความ (โหลดลงเครื่องก่อน)
            await tts.generate_audio(text)

            # 4. รันเสียงและขยับปากพร้อมกัน
            print("🎙️ Lumina กำลังพูด...")
            await asyncio.gather(
                tts.play_audio_async(), # เล่นเสียงออกลำโพง
                lipsync()               # ขยับปากใน VTube Studio
            )
            
    finally:
        # ปิดการเชื่อมต่อเมื่อจบโปรแกรม
        await close_vts()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass