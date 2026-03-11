import asyncio
from tts_engine import TTSEngine
from llm_handler import LLMEngine

tts = TTSEngine()
llm = LLMEngine()

async def main():

    print("--- Lumina AI พร้อมใช้งาน ---")
    print("(พิมพ์ exit เพื่อออก)")

    while True:

        text = input("You: ")

        if not text:
            continue

        if "exit" in text.lower():
            print("ปิดโปรแกรม...")
            break

        answer = await llm.generate(text)

        print("Lumina:", answer)

        # ไม่ต้อง await
        tts.speak(answer)


if __name__ == "__main__":
    asyncio.run(main())