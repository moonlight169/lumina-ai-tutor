import asyncio
import json
import os

import websockets
from dotenv import load_dotenv

VTS_URL = "ws://localhost:8001"
PLUGIN_NAME = "AI-Reception-Robot"
PLUGIN_DEV = "Light"


class VTSClient:
    def __init__(self):
        self.ws: websockets.WebSocketClientProtocol | None = None

    # ---------------------------
    # การเชื่อมต่อ / ปิดการเชื่อมต่อ
    # ---------------------------
    async def connect(self):
        """เชื่อมต่อไปยัง VTube Studio API"""
        self.ws = await websockets.connect(VTS_URL)

    async def close(self):
        """ปิด WebSocket ถ้ามีการเชื่อมต่ออยู่"""
        if self.ws is not None:
            await self.ws.close()
            self.ws = None
            print("🔌 Disconnected from VTS")

    # ---------------------------
    # ฟังก์ชันส่ง request หลัก
    # ---------------------------
    async def _send_request(self, message_type: str, data: dict | None = None):
        if self.ws is None:
            raise RuntimeError("WebSocket ยังไม่ถูก connect()")

        if data is None:
            data = {}

        msg = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": "ai_robot",
            "messageType": message_type,
            "data": data,
        }

        await self.ws.send(json.dumps(msg))
        resp_raw = await self.ws.recv()
        resp = json.loads(resp_raw)
        return resp

    # ---------------------------
    # Helper: จัดการ token ใน .env
    # ---------------------------
    def _clear_token_in_env(self):
        """ลบ VTS_PLUGIN_TOKEN ออกจากไฟล์ .env"""
        if not os.path.exists(".env"):
            return

        lines = []
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip().startswith("VTS_PLUGIN_TOKEN="):
                    lines.append(line)

        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)

    async def _request_new_token(self) -> str:
        """ขอ token ใหม่จาก VTS แล้วเขียนลง .env"""
        print("🔑 ขอ token ใหม่จาก VTS...")
        resp = await self._send_request(
            "AuthenticationTokenRequest",
            {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEV,
            },
        )
        token = resp["data"]["authenticationToken"]

        with open(".env", "a", encoding="utf-8") as f:
            f.write(f"\nVTS_PLUGIN_TOKEN={token}\n")

        print("📌 ได้ token ใหม่และบันทึกลง .env แล้ว")
        print("   ให้กด Allow ใน VTS หน้าต่าง Plugin Permissions หนึ่งครั้ง")
        return token

    # ---------------------------
    # Authentication + Token
    # ---------------------------
    async def authenticate(self):
        """
        โหลด token จาก .env ถ้าไม่มีจะขอใหม่จาก VTS แล้วเขียนลง .env
        จากนั้น authenticate กับ VTS
        ถ้า token ใช้ไม่ได้ (invalid/revoked) จะลบออกแล้วขอใหม่อัตโนมัติ
        """
        load_dotenv()
        token = os.getenv("VTS_PLUGIN_TOKEN")

        # ถ้าไม่มี token เลย -> ขอใหม่
        if token is None:
            token = await self._request_new_token()

        # ลอง authenticate ด้วย token ปัจจุบัน
        resp = await self._send_request(
            "AuthenticationRequest",
            {
                "pluginName": PLUGIN_NAME,
                "pluginDeveloper": PLUGIN_DEV,
                "authenticationToken": token,
            },
        )

        data = resp.get("data", {})
        if data.get("authenticated"):
            print("✅ Authenticated กับ VTube Studio แล้ว")
            return

        # ถ้าไม่ผ่าน ดูเหตุผล
        reason = data.get("reason", "")
        print("❌ Authentication ล้มเหลว:", reason)

        # ถ้า token ใช้ไม่ได้ / โดน revoke -> ขอใหม่อัตโนมัติ
        if "token is invalid or has been revoked" in reason:
            print("⚠ token เดิมใช้ไม่ได้แล้ว -> ลบออกจาก .env และขอใหม่...")
            self._clear_token_in_env()
            token = await self._request_new_token()

            # ลอง auth อีกครั้งด้วย token ใหม่
            resp2 = await self._send_request(
                "AuthenticationRequest",
                {
                    "pluginName": PLUGIN_NAME,
                    "pluginDeveloper": PLUGIN_DEV,
                    "authenticationToken": token,
                },
            )
            if resp2.get("data", {}).get("authenticated"):
                print("✅ Authenticated กับ VTube Studio แล้ว (หลังเปลี่ยน token ใหม่)")
                return
            else:
                raise RuntimeError(f"❌ Authentication ยังล้มเหลวหลังขอ token ใหม่: {resp2}")
        else:
            # ถ้าพังเพราะเหตุผลอื่น ก็โยน error ให้รู้ตัว
            raise RuntimeError(f"❌ Authentication ล้มเหลว: {resp}")

    # ---------------------------
    # การจัดการ Parameter
    # ---------------------------
    async def create_parameter(
        self,
        param_id: str,
        explanation: str = "",
        min_value: float = 0.0,
        max_value: float = 1.0,
        default_value: float = 0.0,
    ):
        """
        สร้าง custom parameter ใหม่ใน VTS (ถ้ามีอยู่แล้ว VTS จะตอบ error เฉย ๆ)
        """
        resp = await self._send_request(
            "ParameterCreationRequest",
            {
                "parameterName": param_id,
                "explanation": explanation,
                "min": min_value,
                "max": max_value,
                "defaultValue": default_value,
            },
        )
        print(f"CreateParameter({param_id}) -> {resp}")
        return resp

    async def set_parameter(self, param_id: str, value: float):
        """
        ส่งค่า parameter เข้าไปให้โมเดล
        เช่น ปากของ Live2D ส่วนใหญ่ใช้ ParamMouthOpenY
        หรือ custom อย่าง AI_Mouth
        """
        resp = await self._send_request(
            "InjectParameterDataRequest",
            {
                "parameterValues": [
                    {"id": param_id, "value": value},
                ]
            },
        )
        return resp
