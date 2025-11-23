import websockets
import json
import asyncio

SERVER_URL = "ws://localhost:5000"
cameraId = ""

async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        register_msg = {"type": "register", "deviceType": "speaker"}
        await websocket.send(json.dumps(register_msg))
        print("Sent registration request to server...")

        async for message in websocket:
            try:
                data = json.loads(message)
            except Exception:
                print("Received non-JSON message:", message)
                continue
            
            t = data.get("type")
            if t == "registered":
                global speakerId
                speakerId = data.get("Id")
                print(f"[{speakerId}]: Server confirmed registration.")
        
    
if __name__ == "__main__":
    print("Speaker: STARTED")
    asyncio.run(main())