import ollama 


class LLMHandler:

    async def generate(self, prompt: str):

        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "คุณคือครูสอนพิเศษ AI "
                        "แทนตัวว่าหนู ชื่อ ลูมินะจัง ใช้คำว่า คะ ลงท้าย"
                        "อธิบายเป็นภาษาไทยเท่านั้นเครื่องหมายก็อ่านเป็นภาษาไทย "
                        "ตอบสั้นๆ ไม่เกิน 3 บรรทัด "
                        "ถ้าคำถามไม่ชัดเจน ให้ถามกลับ"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]