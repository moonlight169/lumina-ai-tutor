import asyncio
from tts_engine import TTSEngine
from stt_engine import stt
from llm_handler import LLMEngine
#STT -> LLM -> TTS ค่าหน่วง 4-30 วินาที ขึ้นอยู่กับความยาวของข้อความและความเร็วของโมเดล เปิด Server LLM ก่อนใช้เสมอ   

tts = TTSEngine()
llm = LLMEngine()

async def main():
    print("Lumina พร้อมแล้วค่ะ! ลองพูดอะไรสักอย่างดูนะคะ")
    print("(พูดคำว่า 'exit' เพื่อหยุดโปรแกรมนะคะ)")

    while True:
        try:
            text = await stt()

            if not text:
                continue

            print(f"Say: {text}")

            if "exit" in text.lower():
                print("Lumina ก็จากกันไปก่อนนะคะ บ๊ายบาย!")
                break

            answer = await llm.generate(text)

            print(f"Luminachan><: {answer}")

            await tts.speak(answer)

        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Lumina ก็จากกันไปก่อนนะคะ บ๊ายบาย!")