import websockets
import json
import asyncio

SERVER_URL = "ws://localhost:5000"
lightId = ""

isOn = False

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
            elif t == "request":
                req = data.get("request")
                if req == "on":
                    global isOn
                    isOn = True
                    print(f"[{lightId}]: Light turned ON.")
                    status_msg = {
                        "type": "status",
                        "Id": lightId,
                        "status": "on"
                    }
                    await websocket.send(json.dumps(status_msg))
                elif req == "off":
                    isOn = False
                    print(f"[{lightId}]: Light turned OFF.")
                    status_msg = {
                        "type": "status",
                        "Id": lightId,
                        "status": "off"
                    }
                    await websocket.send(json.dumps(status_msg))
                elif req == "status":
                    status_msg = {
                        "type": "status",
                        "Id": lightId,
                        "status": "on" if isOn else "off"
                    }
                    await websocket.send(json.dumps(status_msg))
                    print(f"[{lightId}]: Sent status to server.")
                elif req == "color":
                    color = data.get("color")
                    # In actual hardware, program colors here
                    print(f"[{lightId}]: Changed color to {color}.")
        
    
if __name__ == "__main__":
    print("Light: STARTED")
    asyncio.run(main())