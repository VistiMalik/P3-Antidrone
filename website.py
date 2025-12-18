import asyncio
import json
import websockets
import utils.motorUtils as motorUtils
import utils.modes as modes
import utils.rfUtils as rfUtils
import time
import flask
from utils.config import *

h_angle = 10
v_angle = 10
mode = "SETUP"
color = "red"
latitude = 0
longitude = 0
clients = set()


async def broadcast():
    global h_angle, v_angle, mode, color, latitude, longitude

    rssi = rfUtils.getRssi()
    base_diff = rfUtils.getCompValue()
    msg = json.dumps({
        "horizontal_angle": round(h_angle, 1),
        "vertical_angle": round(-90 + v_angle % 360, 1),
        "mode": mode,
        "color": color,
        "rssi": round(rssi, 2) ,
        "base_diff": round(base_diff, 2),
        "lat": latitude,
        "lon": longitude
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
