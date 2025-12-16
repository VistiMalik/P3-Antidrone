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

    msg = json.dumps({
        "horizontal_angle": h_angle,
        "vertical_angle": v_angle,
        "color": color
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
    global h_angle, v_angle, color
    loop = asyncio.get_running_loop()

    while True:
        coords = motorUtils.getCoords()
        print(coords)
        h_angle = coords["horizontal"]
        v_angle = coords["vertical"]
        color = "orange"

        await broadcast()
        await asyncio.sleep(0.2)

async def start_socket():
    async with websockets.serve(handler, "172.20.10.2", 8082):
        print("WebSocket running on ws://172.20.10.2:8082")
        await console_loop()


def start_webpage():
    app = flask.Flask(__name__)

    @app.route('/map')
    def map():
        return flask.send_from_directory('map', 'index.html')

    app.run(host='172.20.10.2', port=8081)
