import asyncio
import json
import websockets

h_angle = 10
v_angle = 10
color = "red"

clients = set()

def state():
    return {"horizontal_angle": h_angle, "vertical_angle": v_angle, "color": color}

async def broadcast():
    if not clients:
        print("No clients connected; nothing to send.")
        return

    msg = json.dumps(state())
    print("Broadcasting:", msg)

    dead = []
    for ws in list(clients):
        try:
            await ws.send(msg)
        except Exception as e:
            print("Send failed:", e)
            dead.append(ws)

    for ws in dead:
        clients.discard(ws)

async def handler(ws):
    clients.add(ws)
    print("Client connected")

    try:
        # Send initial state
        await ws.send(json.dumps(state()))

        async for message in ws:
            print("Received from client:", message)
    finally:
        clients.discard(ws)
        print("Client disconnected")

async def console_loop():
    global h_angle, v_angle, color
    loop = asyncio.get_running_loop()

    while True:
        h = await loop.run_in_executor(None, input, "horizontal: ")
        h_angle = int(h)
        await broadcast()

        v = await loop.run_in_executor(None, input, "vertical:  ")
        v_angle = int(v)
        await broadcast()

        c = await loop.run_in_executor(None, input, "color: ")
        color = c
        await broadcast()

async def main():
    async with websockets.serve(handler, "localhost", 8082):
        print("WebSocket running on ws://localhost:8082")
        await console_loop()

if __name__ == "__main__":
    asyncio.run(main())

