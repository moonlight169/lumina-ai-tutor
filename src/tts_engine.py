import os
import asyncio
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import ElevenLabs


class TTSEngine:

    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=api_key)

        self.voice_id = "9yiczo9fQBjWdt2etT7g" # ค่อยมาแก้

    def _speak_blocking(self, text: str):

        audio_stream = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            text=text
        )

        audio_bytes = b"".join(audio_stream)

        file_path = "tts_temp.mp3"

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        data, samplerate = sf.read(file_path)

        sd.play(data, samplerate)
        sd.wait()

    async def speak(self, text: str):

        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            self._speak_blocking,
            text
        )