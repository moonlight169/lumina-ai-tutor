import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)

print("OpenAI key loaded:", os.getenv("OPENAI_API_KEY") is not None)
print("Gemini key loaded:", os.getenv("GEMINI_API_KEY") is not None)

from src.llm_handler import LLMHandler
from src.tts_engine import TTSEngine


async def tutor():
    """
    Main loop ของ AI Tutor
    รับคำถามจากผู้ใช้ → เรียก LLM → แสดงผล → ส่งให้ TTS พูด
    """

    llm = LLMHandler()
    tts = TTSEngine()

    print("\nAI Tutor พร้อมแล้ว (พิมพ์ 'exit' เพื่อออก)\n")

    while True:
        try:
            question = input("Student: ").strip()

            if question.lower() in ["exit", "quit", "q"]:
                print("Tutor: ลาก่อน!")
                break

            if not question:
                continue

            answer = await llm.generate(question)

            print("\nTutor:", answer, "\n")

            await tts.speak(answer)

            await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\nหยุดโปรแกรม")
            break

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    asyncio.run(tutor())