import asyncio
import numpy as np
from pydub import AudioSegment
import time
from vts_client import VTSClient

PARAM_ID = "AI_Mouth"
MP3_FILE = "tts_temp.mp3"

# สร้าง Client ไว้เป็น Global เพื่อไม่ให้ต้อง Connect ใหม่ทุกรอบ
client = VTSClient()

def audio_to_numpy(audio: AudioSegment):
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)
    
    samples = samples.astype(np.float32)
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples /= max_val
    return samples

async def init_vts():
    """เชื่อมต่อ VTube Studio ครั้งเดียวตอนเปิดโปรแกรม"""
    try:
        await client.connect()
        await client.authenticate()
        print("✅ VTube Studio Connected & Authenticated")
    except Exception as e:
        print(f"❌ VTS Connection Error: {e}")

async def lipsync():
    """วิเคราะห์ไฟล์เสียงและส่งค่าปากแบบ Real-time"""
    try:
        # โหลดไฟล์และเตรียมข้อมูลก่อนเริ่มนับเวลา
        audio = AudioSegment.from_mp3(MP3_FILE)
        samples = audio_to_numpy(audio)
        sample_rate = audio.frame_rate
        
        idx = 0
        block_size = 1024 
        
        # --- เริ่มนับเวลาเพื่อ Sync กับเสียงลำโพง ---
        start_time = time.time()
        
        while idx < len(samples):
            block = samples[idx:idx + block_size]
            volume = np.sqrt(np.mean(block ** 2)) if len(block) > 0 else 0
            
            # ปรับตัวคูณ (3.5) ตามความดังเสียงที่คุณต้องการ
            mouth_value = float(min(volume * 3.5, 1.0))

            # ส่งค่า Parameter ไปยัง VTS
            await client.set_parameter(PARAM_ID, mouth_value)

            idx += block_size

            # คำนวณเวลาที่ควรจะเป็น (Expected) เทียบกับเวลาที่ผ่านไปจริง (Elapsed)
            elapsed = time.time() - start_time
            expected = idx / sample_rate
            
            if expected > elapsed:
                await asyncio.sleep(expected - elapsed)

        # ปิดปากเมื่อจบ
        await client.set_parameter(PARAM_ID, 0.0)
        
    except Exception as e:
        print(f"⚠️ LipSync Error: {e}")

async def close_vts():
    await client.close()