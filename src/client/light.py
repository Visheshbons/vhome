import websockets
import json
import asyncio

SERVER_URL = "ws://localhost:5000"
lightId = ""

async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        register_msg = {"type": "register", "deviceType": "light"}
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
                global lightId
                lightId = data.get("Id")
                print(f"[{lightId}]: Server confirmed registration.")
        
    
if __name__ == "__main__":
    print("Light: STARTED")
    asyncio.run(main())