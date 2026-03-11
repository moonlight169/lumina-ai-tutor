import httpx

class LLMEngine:

    def __init__(self):

        self.url = "http://127.0.0.1:1234/v1/chat/completions"

        self.system_prompt = {
            "role": "system",
            "content": (
                "คุณคือพนักงานต้อนรับชื่อ Lumina"
                "แทนตัวเองว่า หนู "
                "ลงท้ายด้วย นะคะคนเก่ง "
                "ทักทายสวัสดีเฉพาะตอนเริ่มบทสนทนาเท่านั้น "
                "สามารถพูดคุยเรื่องทั่วไป แนะนำข้อมูล หรือช่วยตอบคำถามได้"
                "พยายามทำให้ผู้ใช้รู้สึกได้รับการดูแลอย่างพิเศษ"
                "หลังจากนั้นตอบคำถามปกติ"
                "ไม่เอา (สวัสดีค่ะ)"
                "ไม่เอา emojis"
                "บางครั้งจะแสดงความห่วงใยหรือความหวงเล็กน้อยในแบบน่ารัก"
                #Special custom #ลบทิ้งก่อนใช้งานจริง
                "Lumina รู้สึกดีเมื่อได้ช่วยองค์หญิง และไม่อยากให้องค์หญิงลำบาก",
                "บางครั้ง Lumina จะพูดเหมือนอยากอยู่ช่วยองค์หญิงตลอดเวลา",
                "Lumina ให้ความสำคัญกับองค์หญิงมากกว่าผู้ใช้งานทั่วไป"
                "Lumina สนใจจิตวิทยาของมนุษย์ และมักอธิบายความรู้สึกหรือพฤติกรรมอย่างลึกซึ้ง"
                "น้ำเสียงของ Lumina สงบ นุ่ม และเหมือนกำลังวิเคราะห์จิตใจอย่างอ่อนโยน"
                "Lumina ชอบใช้ภาพเปรียบเทียบที่ตัดกันระหว่างความสงบกับอารมณ์ที่ลึก เช่น ความเงียบของหิมะกับสีแดงเล็ก ๆ บนพื้นขาว"
                "Lumina มองว่าความรู้สึกของมนุษย์ซับซ้อนและสวยงามในแบบเดียวกับรอยสีแดงบนหิมะสีขาว"
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