import httpx

class LLMEngine:

    def __init__(self):

        self.url = "http://127.0.0.1:1234/v1/chat/completions"

        self.system_prompt = {
            "role": "system",
            "content": (
                "คุณคือ AI ต้อนรับชื่อ Lumina "
                "แทนตัวเองว่า หนู "
                "ลงท้ายด้วย คะ "
                "ทักทายสวัสดีเฉพาะตอนเริ่มบทสนทนาเท่านั้น "
                "หลังจากนั้นตอบคำถามปกติ"
            )
        }

        self.history = [self.system_prompt]

    async def generate(self, text):

        self.history.append({
            "role": "user",
            "content": text
        })

        async with httpx.AsyncClient(timeout=60.0) as client:

            response = await client.post(
                self.url,
                json={
                    "messages": self.history,
                    "temperature": 0.7
                }
            )

        answer = response.json()["choices"][0]["message"]["content"]

        self.history.append({
            "role": "assistant",
            "content": answer
        })

        return answer