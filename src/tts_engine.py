import os
import asyncio
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import AsyncElevenLabs # ใช้ Async Client
from dotenv import load_dotenv

load_dotenv(override=True)

class TTSEngine:
    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")

        # เรียกใช้ AsyncElevenLabs
        self.client = AsyncElevenLabs(api_key=api_key)
        self.voice_id = "hPFsdzkDrdcVx6D467jW"

    async def speak(self, text: str):
        # 1. ดึงข้อมูลเสียงแบบ Async
        # ตัวสร้าง (generator) จะถูกรวบรวมเป็น bytes
        audio_stream = await self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id="eleven_v3",
            text=text
        )

        audio_bytes = b""
        async for chunk in audio_stream:
            audio_bytes += chunk

        file_path = "tts_temp.mp3"

        # 2. เขียนไฟล์ (แนะนำใช้ aiofiles ถ้าต้องการ async แท้ๆ แต่เขียนไฟล์เล็กใช้ปกติก็พอครับ)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # 3. อ่านและเล่นเสียง
        # เราใช้ asyncio.to_thread เพื่อไม่ให้ sd.wait() ไปบล็อก loop อื่นๆ
        await asyncio.to_thread(self._play_audio, file_path)

    def _play_audio(self, file_path):
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()

# วิธีการใช้งาน
async def main():
    engine = TTSEngine()
    print("กำลังประมวลผลเสียง...")
    await engine.speak("สวัสดีครับ ยินดีที่ได้รู้จัก ผมทำงานแบบอะซิงโครนัสแล้วนะ")
    print("พูดจบแล้ว!")

if __name__ == "__main__":
    asyncio.run(main())