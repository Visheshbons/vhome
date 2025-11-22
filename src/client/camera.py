import websockets
import json
import asyncio

SERVER_URL = "ws://localhost:5000"
cameraId = ""

async def main(ws):
    register_msg = {"type": "register", "deviceType": "camera"}
    await ws.send(json.dumps(register_msg))
    print("Sent registration request to server...")

    async for message in ws:
        try:
            data = json.loads(message)
        except Exception:
            print("Recieved non-JSON message:", message)
        
        t = data.get("type")
        if t == "registered":
            global cameraId
            cameraId = data.get("cameraId")
            print(f"[{cameraId}]: Server confirmed registration.")
        
    
if __name__ == "__main__":
    print("Camera: STARTED")
    asyncio.run(main())