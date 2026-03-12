import asyncio
from tts_engine import TTSEngine
from stt_engine import stt
from vtube_bridge import lipsync, init_vts, close_vts
from llm_handler import LLMHandler

llm = LLMHandler()
tts = TTSEngine()


async def main():
    await init_vts()

    # warmup ลด delay ครั้งแรก
    print("🔥 Warming up LLM...")
    await llm.get_response("สวัสดี")

    while True:
        # 1. ฟัง
        text = await stt()
        if not text:
            continue

        if "exit" in text.lower():
            break

        print(f"🎤 User: {text}")

        # 2. เริ่มให้ LLM คิดทันที
        llm_task = asyncio.create_task(
            llm.get_response(text)
        )

        # รอคำตอบ
        response_text = await llm_task

        print(f"🤖 Lumina: {response_text}")

        # 3. สร้างเสียง
        tts_task = asyncio.create_task(
            tts.generate_gtts(response_text)
        )

        await tts_task

        # 4. เล่นเสียง + lipsync พร้อมกัน
        await asyncio.gather(
            tts.play_audio_async(),
            lipsync()
        )

    await close_vts()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass