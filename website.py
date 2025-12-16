import asyncio
import json
import websockets
import utils.motorUtils as motorUtils
import time
import flask

h_angle = 10
v_angle = 10
color = "red"

clients = set()


async def broadcast():
    global h_angle, v_angle, color

    msg = '{"horizontal_angle": {}, "vertical_angle": {}, "color": {}}'.format(h_angle, v_angle, color)
    for ws in list(clients):
         await ws.send(msg)


async def handler(ws):
    clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        clients.remove(ws)


async def console_loop():
    global h_angle, v_angle, color
    loop = asyncio.get_running_loop()

    while True:
        cords = motorUtils.getCoords()
        h_angle = cords["horizontal"]
        v_angle = cords["vertical"]
        color = "lime"

        await broadcast()
        asyncio.sleep(0.2)

async def start_socket():
    async with websockets.serve(handler, "localhost", 8082):
        print("WebSocket running on ws://localhost:8082")
        await console_loop()


def start_webpage():
    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        return flask.send_from_directory('web', 'index.html')

    app.run(host='127.0.0.1', port=8081)