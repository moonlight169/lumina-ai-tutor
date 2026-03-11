import os
import asyncio
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import AsyncElevenLabs
from dotenv import load_dotenv

load_dotenv(override=True)

class TTSEngine:
    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")

        self.client = AsyncElevenLabs(api_key=api_key)
        self.voice_id = "hPFsdzkDrdcVx6D467jW"
        self.temp_file = "tts_temp.mp3"

    async def generate_audio(self, text: str):
        """Step 1: โหลดเสียงจาก ElevenLabs และเซฟลงไฟล์ (ยังไม่เล่น)"""
        print("⏳ Generating audio from ElevenLabs...")
        audio_stream = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id="eleven_v3",
            text=text
        )

        audio_bytes = b""
        async for chunk in audio_stream:
            if chunk:
                audio_bytes += chunk

        with open(self.temp_file, "wb") as f:
            f.write(audio_bytes)
        print("✅ Audio file ready.")

    async def play_audio_async(self):
        """Step 2: เล่นเสียงแบบไม่บล็อก (Async Thread)"""
        await asyncio.to_thread(self._play_audio)

    def _play_audio(self):
        data, samplerate = sf.read(self.temp_file)
        sd.play(data, samplerate)
        sd.wait() # รอจนกว่าเสียงจะจบใน Thread นี้