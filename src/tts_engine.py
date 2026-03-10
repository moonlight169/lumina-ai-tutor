import os
import sounddevice as sd
import soundfile as sf
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv(override=True)


class TTSEngine:

    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")

        self.client = ElevenLabs(api_key=api_key)

        self.voice_id = "hPFsdzkDrdcVx6D467jW"

    def speak(self, text: str):

        audio_stream = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            model_id="eleven_v3",
            text=text
        )

        audio_bytes = b"".join(audio_stream)

        file_path = "tts_temp.mp3"

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        data, samplerate = sf.read(file_path)

        sd.play(data, samplerate)
        sd.wait()