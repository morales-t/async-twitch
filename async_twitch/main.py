
from websocket import websocketsconnect
import asyncio
import os


loop = asyncio.get_event_loop()
user = os.environ.get('TWITCH_USER')
password = os.environ.get('TWITCH_PASS')
websocket = websocketsconnect(user, password, loop)
loop.run_until_complete(websocket.connect())
loop.create_task(websocket.join_channel('mizkif'))
loop.run_until_complete(websocket.listen())
