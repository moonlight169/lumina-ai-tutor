import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    def __init__(self):
        # ตั้งค่า API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # 1. ค้นหาโมเดลอัตโนมัติ (ที่คุณรันผ่านเมื่อกี้)
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        selected_model = ""
        for target in ['flash', 'pro', 'gemini']:
            for name in available_models:
                if target in name.lower():
                    selected_model = name
                    break
            if selected_model: break
        
        if not selected_model: selected_model = available_models[0]
        print(f"✅ Selected Model: {selected_model}")
        
        self.model = genai.GenerativeModel(selected_model)
        self.system_prompt = (
            "คุณคือ Lumina AI ผู้ช่วยต้อนรับเสมือนจริงของสถานศึกษา "
            "ตอบเป็นภาษาไทย สั้น กระชับ เป็นกันเอง และสุภาพ"
        )

    # ✅ ตรวจสอบชื่อฟังก์ชันนี้ ต้องชื่อ get_response และอยู่ภายใต้ Class
    async def get_response(self, user_input: str):
        try:
            full_prompt = f"{self.system_prompt}\n\nผู้ใช้งานพูดว่า: {user_input}\nLumina ตอบว่า:"
            
            # เรียกใช้งานแบบ Non-blocking
            response = await asyncio.to_thread(
                self.model.generate_content, full_prompt
            )
            
            return response.text.strip()
        except Exception as e:
            print(f"❌ LLM Error inside handler: {e}")
            return "ขออภัยค่ะ ฉันคิดคำตอบไม่ทัน รบกวนลองใหม่อีกครั้งนะคะ"