import asyncio
from tts_engine import TTSEngine
from stt_engine import stt
from vtube_bridge import lipsync, init_vts, close_vts

from llm_handler import LLMHandler
llm = LLMHandler()

# สร้าง Instance ของ TTS
tts = TTSEngine()

async def main():
    await init_vts()
    
    while True:
        text = await stt() # 1. ฟัง
        if not text: continue
        if "exit" in text.lower(): break
        print(f"🎤 User: {text}")

        # 2. คิด (ส่งไปหา Gemini)
        response_text = await llm.get_response(text)
        print(f"🤖 Lumina: {response_text}")

        # 3. พูดและขยับ (TTS + LipSync)
        await tts.generate_audio(response_text)
        await asyncio.gather(
            tts.play_audio_async(),
            lipsync()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass