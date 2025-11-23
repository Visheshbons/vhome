import websockets
import json
import asyncio

SERVER_URL = "ws://localhost:5000"
speakerId = ""


async def handle_server_messages(websocket, registered_event, confirmation_event):
    global speakerId
    async for message in websocket:
        try:
            data = json.loads(message)
        except Exception:
            print("Received non-JSON message:", message)
            continue
        t = data.get("type")
        if t == "registered":
            speakerId = data.get("Id")
            print(f"[{speakerId}]: Server confirmed registration. You may now enter commands.")
            registered_event.set()
        elif t == "confirmed":
            req = data.get("request")
            status = data.get("status")
            if req in ("lightOn", "lightOff"):
                state = "ON" if status == "on" else "OFF"
                print(f"[CONFIRMED]: Lights {state}.")
            else:
                print("[CONFIRMED]:", data)
            confirmation_event.set()  # Unblock prompt
        else:
            print("[SERVER MESSAGE]:", data)


async def prompt_loop(websocket, registered_event, confirmation_event):
    global speakerId
    await registered_event.wait()  # wait until registration completed
    loop = asyncio.get_event_loop()
    while True:
        await confirmation_event.wait()  # wait for previous confirmation
        prompt = await loop.run_in_executor(None, input, "Command (light on/off, exit): ")
        if prompt is None:
            continue
        p = prompt.strip().lower()
        if p in ("exit", "quit"):
            print("Exiting prompt loop...")
            await websocket.close()
            break
        if p in ("light on", "light off"):
            if not speakerId:
                print("Waiting for registration before sending requests...")
                continue
            confirmation_event.clear()  # Block next prompt until confirmed
            request_value = "lightOn" if p == "light on" else "lightOff"
            request_msg = {
                "type": "request",
                "deviceType": "speaker",
                "request": request_value,
            }
            try:
                await websocket.send(json.dumps(request_msg))
                state = "ON" if request_value == "lightOn" else "OFF"
                print(f"[{speakerId}]: Sent light {state} request. Awaiting confirmation...")
            except Exception as e:
                print("Error sending request:", e)
                confirmation_event.set()  # Unblock on error
        else:
            print("Unknown command. Use 'light on', 'light off', or 'exit'.")


async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        register_msg = {"type": "register", "deviceType": "speaker"}
        await websocket.send(json.dumps(register_msg))
        print("Sent registration request to server... Waiting for confirmation...")

        registered_event = asyncio.Event()
        confirmation_event = asyncio.Event()
        confirmation_event.set()  # Initially ready for first command
        server_task = asyncio.create_task(handle_server_messages(websocket, registered_event, confirmation_event))
        prompt_task = asyncio.create_task(prompt_loop(websocket, registered_event, confirmation_event))

        done, pending = await asyncio.wait(
            {server_task, prompt_task}, return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        if not websocket.closed:
            await websocket.close()
        print("Connection closed.")


if __name__ == "__main__":
    print("Speaker: STARTED")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user.")