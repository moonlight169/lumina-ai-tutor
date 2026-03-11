import httpx
import os
from dotenv import load_dotenv

load_dotenv(override=True)


class LLMEngine:

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:1234",
        model: str = "gemma-3-4b",
        timeout: float = 30.0,
    ):
        self.url = f"{base_url}/v1/chat/completions"
        self.model = model
        self.timeout = timeout

        self.client = httpx.AsyncClient(timeout=self.timeout)

        self.system_prompt = (
            "คุณคือ AI ผู้ช่วยต้อนรับชื่อ Lumina "
            "แทนตัวเองว่า หนู "
            "ใช้คำลงท้ายว่า คะ "
            "พูดภาษาไทยสุภาพ เป็นมิตร "
            "ตอบสั้นไม่เกิน 2-3 ประโยค "
            "เหมาะกับการอ่านออกเสียง"
        )

    async def generate(self, user_text: str) -> str:

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_text},
            ],
            "temperature": 0.7,
            "max_tokens": 120,
        }

        try:
            response = await self.client.post(self.url, json=payload)
            response.raise_for_status()

            data = response.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print("LLM error:", e)
            return "หนูไม่สามารถตอบได้คะ ถามใหม่อีกครั้งนะคะ รอบนี้หนูจะตั้งใจฟังนะคะคนเก่ง"

    async def close(self):
        await self.client.aclose()