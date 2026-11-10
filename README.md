# 🌟 Lumina AI Tutor (ลูมิน่า)

**ลูมิน่า (Lumina)** คือผู้ช่วยเสมือนจริง (AI VTuber) ประจำแผนกเทคโนโลยีคอมพิวเตอร์ วิทยาลัยเทคนิคกาฬสินธุ์
ผู้มาเยี่ยมชมพูดถามเป็นภาษาไทยได้เลย แล้วลูมิน่าจะตอบด้วยเสียง พร้อมขยับปากตัวละคร Live2D ใน VTube Studio แบบเรียลไทม์

ลูมิน่าตอบคำถามเกี่ยวกับแผนกได้ เช่น หลักสูตร ปวช./ปวส. รายชื่อคณะครู สถานที่ ห้องน้ำ Wi-Fi ผลงานของแผนก และการสมัครเรียน

---

## ✨ ความสามารถ

- 🎤 **ฟังเสียงภาษาไทย (STT)**: ใช้ `faster-whisper` กับโมเดล Thonburian Whisper large-v3 บน GPU และหยุดอัดเสียงเองเมื่อผู้พูดเงียบ
- 🧠 **คิดคำตอบด้วย LLM ในเครื่อง**: ใช้ [Ollama](https://ollama.com) กับโมเดล `gemma3:4b` พร้อม System Prompt ที่ใส่ข้อมูลแผนกไว้แล้ว
- 🔊 **พูดตอบ (TTS)**: ใช้ ElevenLabs (`eleven_v3`) และมี gTTS เป็นตัวสำรอง
- 👄 **ขยับปาก (Lip-sync)**: วัดความดังของไฟล์เสียง แล้วส่งค่าไปที่ VTube Studio ผ่าน WebSocket API ให้ปากขยับตรงกับเสียงที่เล่น

## 🔄 การทำงาน

```
 ไมโครโฟน ──▶ STT (faster-whisper) ──▶ LLM (Ollama) ──▶ TTS (ElevenLabs)
                                                            │
                                         ┌──────────────────┴──────────────────┐
                                         ▼                                     ▼
                                  เล่นเสียงทางลำโพง               Lip-sync ──▶ VTube Studio
                                         └────────── ทำงานพร้อมกัน (asyncio) ──────────┘
```

เมื่อเปิดโปรแกรม ระบบจะเชื่อมต่อ VTube Studio และ warm-up LLM ก่อน จากนั้นจะวนรับคำถามไปเรื่อยๆ จนกว่าผู้ใช้จะพูดคำว่า `exit`

## 📁 โครงสร้างโปรเจค

```
lumina-ai-tutor/
├── environment.yml        # Conda environment (Python 3.10 + PyTorch CUDA 12.1)
├── src/
│   ├── main.py            # ลูปหลัก: ฟัง → คิด → พูด + ขยับปาก
│   ├── stt_engine.py      # อัดเสียงจากไมค์ + ถอดความด้วย Whisper
│   ├── llm_handler.py     # เรียก Ollama + System Prompt ของลูมิน่า
│   ├── tts_engine.py      # สร้างเสียง (ElevenLabs / gTTS) และเล่นเสียง
│   ├── vtube_bridge.py    # คำนวณค่าปากจากไฟล์เสียงแล้วส่งไป VTS
│   ├── vts_client.py      # WebSocket client ของ VTube Studio API (auth + token)
│   └── async_pipeline.py  # (ยังว่าง: สำรองไว้สำหรับ pipeline แบบ streaming)
└── LICENSE
```

## 🧰 สิ่งที่ต้องมี

| รายการ | หมายเหตุ |
|---|---|
| NVIDIA GPU + CUDA 12.x | STT ตั้งค่าไว้ที่ `device="cuda"`, `float16` (ทดสอบกับ RTX 40 series) |
| [Miniconda / Anaconda](https://docs.conda.io) | สำหรับสร้าง environment |
| [Ollama](https://ollama.com) | ต้องรันอยู่ที่ `http://localhost:11434` |
| [VTube Studio](https://denchisoft.com) | ต้องเปิด API ที่พอร์ต `8001` และมีโมเดล Live2D |
| ElevenLabs API Key | สำหรับเสียงพูด |
| ไมโครโฟน + ลำโพง | |

## 🚀 การติดตั้ง

**1. Clone และสร้าง environment**

```bash
git clone https://github.com/moonlight169/lumina-ai-tutor.git
cd lumina-ai-tutor
conda env create -f environment.yml
conda activate edu-buddy-ai
```

**2. ดาวน์โหลดโมเดล LLM**

```bash
ollama pull gemma3:4b
```

**3. สร้างไฟล์ `.env`** ไว้ในโฟลเดอร์ `src/`

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

> `VTS_PLUGIN_TOKEN` ไม่ต้องใส่เอง โปรแกรมจะขอ token จาก VTube Studio แล้วเขียนลง `.env` ให้อัตโนมัติ
> ไฟล์ `.env` อยู่ใน `.gitignore` แล้ว **ห้าม commit ขึ้น Git**

**4. ตั้งค่า VTube Studio**

1. เปิด **Settings → Start API (allow plugins)** โดยใช้พอร์ต `8001`
2. ต้องมี custom parameter ชื่อ **`AI_Mouth`** (ค่า 0–1) แล้วผูกเข้ากับ `ParamMouthOpenY` ของโมเดล
   (สร้างได้ด้วยเมธอด `VTSClient.create_parameter("AI_Mouth")` ใน `vts_client.py`)
3. ตอนรันครั้งแรกจะมีหน้าต่าง Plugin Permissions ขึ้นมา ให้กด **Allow**

## ▶️ การใช้งาน

```bash
cd src
python main.py
```

- รอให้ขึ้น `🎤 Listening...` แล้วพูดคำถามได้เลย พูดจบแล้วเงียบไว้สักครู่ ระบบจะส่งคำถามเอง
- พูดคำว่า **`exit`** หรือกด `Ctrl+C` เพื่อออกจากโปรแกรม
- ทดสอบ STT อย่างเดียวได้ด้วยคำสั่ง `python stt_engine.py`

> การรันครั้งแรกจะดาวน์โหลดโมเดล Whisper (หลาย GB) ซึ่งอาจใช้เวลานานพอสมควร

## ⚙️ ปรับแต่ง

| สิ่งที่ปรับได้ | ไฟล์ | ค่า |
|---|---|---|
| ความไวไมค์ / เวลาเงียบที่ถือว่าพูดจบ | `stt_engine.py` | `SILENCE_THRESHOLD`, `SILENCE_DURATION` |
| โมเดล STT | `stt_engine.py` | `MODEL_SIZE` |
| โมเดล LLM / ข้อมูลและบุคลิกของลูมิน่า | `llm_handler.py` | `model_name`, `system_prompt` |
| เสียงพูด | `tts_engine.py` | `voice_id`, `model_id` |
| ความกว้างของการขยับปาก | `vtube_bridge.py` | ตัวคูณ `volume * 3.5` |

## 🛠️ แก้ปัญหาเบื้องต้น

- **`Connection Error` จาก LLM**: ตรวจว่า Ollama รันอยู่ และดาวน์โหลด `gemma3:4b` แล้ว
- **`ELEVENLABS_API_KEY not set`**: ตรวจว่ามีไฟล์ `src/.env` และรันโปรแกรมจากในโฟลเดอร์ `src`
- **`VTS Connection Error`**: ตรวจว่าเปิด VTube Studio และเปิด API ที่พอร์ต 8001 แล้ว
- **ปากไม่ขยับ**: ตรวจว่ามี parameter `AI_Mouth` และผูกกับปากของโมเดลแล้ว
- **Error เรื่อง cuBLAS / cuDNN DLL**: ตรวจว่าติดตั้ง `nvidia-cublas-cu12` และ `nvidia-cudnn-cu12` ใน environment แล้ว
- **อ่านไฟล์ mp3 ไม่ได้**: ต้องมี `ffmpeg` (มีอยู่ใน `environment.yml` แล้ว)

## 📄 License

[MIT](LICENSE) © 2026 light
