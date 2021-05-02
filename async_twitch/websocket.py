from sqlalchemy import create_engine
from constants import DATABASE_LOCATION
from sql_dao import upload_data
import websockets as ws
import datetime as dt
import asyncio
import re


class websocketsconnect:
    def __init__(self, nick, password, loop: asyncio.BaseEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.nick = nick.lower()
        self.password = password
        self.twitchurl = 'wss://irc-ws.chat.twitch.tv:443'
        self._ws = None
        self.joined_channels = []
        self.authed = False
        self.lower_channel = None
        self.engine = create_engine(f'sqlite:///{DATABASE_LOCATION}')

    async def connect(self):
        if await self.is_connected():
            pass
        else:
            self._ws = await ws.connect(self.twitchurl)
            await self.auth()
        return self._ws

    async def is_connected(self):
        return self._ws is not None and self._ws.open

    async def auth(self):
        await self.connect()
        await self._ws.send(f'PASS oauth:{self.password}')
        await self._ws.send(f'NICK {self.nick}')
        self.authed = True

    async def join_channel(self, channel):
        await self.connect()

        self.lower_channel = channel.lower()
        if self.lower_channel in self.joined_channels:
            pass
        else:
            await self._ws.send(f'JOIN #{self.lower_channel}')
            self.joined_channels.append(channel)

    async def listen(self):
        await self.connect()
        lister = []
        messages = 0

        while True:
            msg = await self._ws.recv()
            msg = await self.process_message(msg)

            if msg is not None:
                lister.append(msg)
                messages += 1

            if messages >= 50:
                await self.loop.run_in_executor(
                        None,
                        lambda: upload_data(self.engine, lister)
                )
                lister = []
                messages = 0

    async def process_message(self, msg):
        if msg == 'PING :tmi.twitch.tv\r\n':
            await self._ws.send('PONG :tmi.twitch.tv')

        regex_string = re.match(
            ":(?P<author>[a-z0-9_]*?)!(?P=author)@(?P=author)"
            ".tmi.twitch.tv PRIVMSG #(?P<channel>[a-z0-9_]*?) :(?P<message>.*)"
            "\r\n",
            msg,
            flags=re.IGNORECASE)

        try:
            author = regex_string.group('author')
            message = regex_string.group('message')
            channel = regex_string.group('channel')
            date_time = dt.datetime.now()

        except AttributeError:
            author = None
            message = None
            channel = None
            date_time = None

        if author is None and message is None:
            final_message = None
        else:
            final_message = {
                'author': author,
                'channel': channel,
                'message': message,
                'date_processed': date_time
            }

        return final_message
