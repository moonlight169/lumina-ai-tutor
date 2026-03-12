import os
import sys
import asyncio
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel, download_model

# --- DLL Configuration (สำหรับ Windows/CUDA) ---
if sys.platform == 'win32':
    base_path = sys.prefix 
    dll_paths = [
        os.path.join(base_path, "Library", "bin"),
        os.path.join(base_path, "Lib", "site-packages", "nvidia", "cublas", "bin"),
        os.path.join(base_path, "Lib", "site-packages", "nvidia", "cudnn", "bin"),
    ]
    for path in dll_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- Constants ---
SAMPLE_RATE = 16000
MODEL_SIZE = "medium"  # เลือกขนาดโมเดลที่ต้องการ (tiny, base, small, medium, large-v3)
# ตั้งค่าความดังขั้นต่ำ (0.01 - 0.05) และเวลาที่เงียบ (วินาที)
SILENCE_THRESHOLD = 0.02  # ปรับเพิ่มถ้าเสียงรบกวนในห้องเยอะ
SILENCE_DURATION = 0.6   # พูดจบแล้วเงียบเกิน 0.6 วินาที จะถือว่าพูดเสร็จ

# --- Global Model Initialization ---
print(f"📦 Checking/Downloading model: {MODEL_SIZE}...")
model_path = download_model(MODEL_SIZE) 
model = WhisperModel(
    model_path,
    device="cuda",
    compute_type="float16",
    cpu_threads=4,
    num_workers=1
)
print("✅ Model loaded and ready!")

async def record_until_silent():
    """ฟังก์ชันอัดเสียงที่จะหยุดเองอัตโนมัติเมื่อผู้ใช้พูดจบ"""
    loop = asyncio.get_event_loop()
    audio_buffer = []
    
    print("\n🎤 Listening... (พูดจบแล้วเงียบไว้สักครู่เพื่อส่งข้อมูล)")
    
    is_speaking = False
    last_active_time = loop.time()
    
    def callback(indata, frames, time, status):
        nonlocal is_speaking, last_active_time
        if status:
            print(status)
        
        # ตรวจสอบความดัง (Amplitude) ของเสียงก้อนปัจจุบัน
        amplitude = np.max(np.abs(indata))
        
        if amplitude > SILENCE_THRESHOLD:
            is_speaking = True
            last_active_time = loop.time()
        
        audio_buffer.append(indata.copy())

    # เริ่ม Stream รับเสียงจากไมโครโฟน
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while True:
            await asyncio.sleep(0.1)
            
            # ถ้าเริ่มมีการพูดแล้ว และเงียบไปนานกว่าที่กำหนด
            if is_speaking and (loop.time() - last_active_time > SILENCE_DURATION):
                break
            
            # ป้องกันการอัดค้างนานเกินไป (เช่น กรณี Noise ดังตลอด)
            if loop.time() - last_active_time > 10 and not is_speaking:
                break

    print("🛑 Speech finished. Processing...")
    return np.concatenate(audio_buffer).flatten()

async def transcribe_audio(audio_data):
    """ฟังก์ชันถอดความแบบ Asynchronous"""
    loop = asyncio.get_event_loop()

    def run_transcription():
        segments, _ = model.transcribe(
            audio_data,
            language="th", 
            vad_filter=True, # ใช้ VAD ภายในของ Whisper ช่วยอีกชั้น
            beam_size=1
        )
        return "".join([seg.text for seg in segments]).strip()

    return await loop.run_in_executor(None, run_transcription)

async def stt():
    """ลูปหลักที่รอรับเสียงแล้วคืนค่ากลับ"""
    try:
        audio_data = await record_until_silent()
        
        # กรองเสียงที่สั้นเกินไปทิ้ง (เพื่อป้องกัน Noise)
        if len(audio_data) < SAMPLE_RATE * 0.5:
            return None
            
        result = await transcribe_audio(audio_data)
        return result
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    async def main():
        try:
            while True:
                transcription = await stt()
                if transcription:
                    print(f"📝 Transcription: {transcription}")
                else:
                    print("... (No clear speech detected) ...")
        except KeyboardInterrupt:
            print("\n👋 Stop program")

    asyncio.run(main())