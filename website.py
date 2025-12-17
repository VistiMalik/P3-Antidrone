import asyncio
import json
import websockets
import utils.motorUtils as motorUtils
import utils.modes as modes
import time
import flask
from utils.config import *

h_angle = 10
v_angle = 10
mode = "SETUP"
color = "red"

clients = set()


async def broadcast():
    global h_angle, v_angle, mode, color

    msg = json.dumps({
        "horizontal_angle": h_angle,
        "vertical_angle": (-90 + v_angle % 360),
        "mode": mode,
        "color": color,
    })
    for ws in list(clients):
         await ws.send(msg)


async def handler(ws):
    clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        clients.remove(ws)


async def console_loop():
    global h_angle, v_angle, mode, color
    loop = asyncio.get_running_loop()

    while True:
        coords = motorUtils.getCoords()
        mode = modes.getCurrentMode()
        
        print(coords)
        print(mode)
        h_angle = coords["horizontal"]
        v_angle = coords["vertical"]
        if mode == 0: color = "blue"; mode = "SETUP"
        elif mode == 1: color = "lime"; mode = "IDLE"
        elif mode == 2: color = "orange"; mode = "SEARCH"
        elif mode == 3: color = "red"; mode = "JAMMING"
        else: color = "white"; mode = "UNKNOWN"

        await broadcast()
        await asyncio.sleep(0.05)

async def start_socket():
    async with websockets.serve(handler, IP, 8082):
        print(f"WebSocket running on ws://{IP}:8082")
        await console_loop()


def start_webpage():
    app = flask.Flask(__name__)

    @app.route('/map')
    def map():
        return flask.render_template('map/index.html', ip=IP)

    app.run(host=IP, port=8081)
