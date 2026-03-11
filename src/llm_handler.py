import asyncio
import requests
import json

class LLMHandler:
    def __init__(self):
        # ตั้งค่าพื้นฐานสำหรับ Ollama
        self.url = "http://localhost:11434/api/generate"
        self.model_name = "gemma3:4b"  # มั่นใจว่าโหลดตัวนี้มาแล้ว
        
        # กำหนดบุคลิกของ Lumina
        self.system_prompt = (
            "คุณคือ Lumina AI ผู้ช่วยต้อนรับเสมือนจริงของสถานศึกษา "
            "ตอบเป็นภาษาไทย สั้น กระชับ เป็นกันเอง และสุภาพ "
            "ห้ามตอบยาวเกิน 2 ประโยค"
        )
        print(f"✅ Local Brain Ready: {self.model_name}")

    async def get_response(self, user_input: str):
        try:
            # เตรียมข้อมูลส่งให้ Ollama
            payload = {
                "model": self.model_name,
                "prompt": f"{self.system_prompt}\n\nผู้ใช้งานพูดว่า: {user_input}\nLumina ตอบว่า:",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }

            # เรียกใช้งานแบบ Non-blocking เพื่อไม่ให้ GUI ค้าง
            response = await asyncio.to_thread(
                requests.post, 
                self.url, 
                json=payload, 
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"❌ Ollama Error: Status {response.status_code}")
                return "ขออภัยค่ะ สมองของฉันขัดข้องเล็กน้อย ลองใหม่อีกครั้งนะคะ"

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return "ขออภัยค่ะ ฉันเชื่อมต่อกับสมองส่วนกลางไม่ได้ รบกวนตรวจสอบ Ollama นะคะ"