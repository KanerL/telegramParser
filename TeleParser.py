import asyncio
import os
import threading

from telethon import TelegramClient, events, sync
from telethon.hints import Entity
from telethon.tl.types import PeerChat, Channel, Dialog

api_id = 1103463
api_hash = '91971674d49ac402c515c2a85957c032'
filter_filename = 'filters.txt'
urls_filename = 'urls.txt'
id_file = 'id_file.txt'
lock = threading.Lock()
redirect_to = 'me'

class TeleParser:
    filters = []
    urls = []
    id_of_urls = []

    def __init__(self, loop, api_id, api_hash, filter_file, ursl_file, id_file):
        self.loop = loop
        self.title = 'title'
        self.api_id = api_id
        self.api_hash = api_hash
        self.filter_file = filter_file
        self.urls_file = ursl_file
        self.id_file = id_file
        self.load_filters()
        self.load_urls()
        self.load_id_of_urls()
        self.run()

    def load_filters(self):
        if os.path.isfile(self.filter_file):
            with open(self.filter_file, encoding='utf-8') as inf:
                filters = [x.strip() for x in inf.readlines()]
        else:
            with open(self.filter_file, mode='w', encoding='utf-8') as ouf:
                pass
            filters = []
        self.filters = filters

    def load_urls(self):
        if os.path.isfile(self.urls_file):
            with open(self.urls_file, encoding='utf-8') as inf:
                urls = []
                for x in inf.readlines():
                    if x.startswith('t.me/') or x.startswith('t.me/joinchat/'):
                        urls.append(x.strip())
                    else:
                        raise ValueError(f'{x} не отформатирована по виду t.me/link или t.me/joinchat/link')
        else:
            with open(self.urls_file, mode='w', encoding='utf-8') as ouf:
                pass
            urls = []
        print(urls)
        self.urls = urls

    def load_id_of_urls(self):
        if os.path.isfile(self.id_file):
            with open(self.id_file, encoding='utf-8') as inf:
                id_of_urls = [x.strip().split(':') for x in inf.readlines()]
        else:
            with open(self.id_file, mode='w', encoding='utf-8') as ouf:
                pass
            id_of_urls = []
        self.id_of_urls = id_of_urls

    def update_urls_id(self,client):
        asd = client.get_dialogs()
        channels_list = {d.entity.id:f't.me/{d.entity.username}'
                         for d in asd
                         if d.is_channel and f't.me/{d.entity.username}' in self.urls}
        for url in self.urls:
            if url not in channels_list.values():
                channels_list[client.get_entity(url).id] = url
        self.id_of_urls = channels_list

    def run_tele(self, loop):

        asyncio.set_event_loop(loop)
        with TelegramClient('name', self.api_id, self.api_hash, loop=loop) as client:
            # loading
            client.send_message('me', 'Hello, myself!')
            print(client.download_profile_photo('me'))
            client: TelegramClient
            self.update_urls_id(client)
            print(self.id_of_urls)
            ch : Channel
            # print(channels['asdasdasdas'].__dict__)

            @client.on(events.NewMessage(incoming=True))
            async def handler(event: events.newmessage.NewMessage.Event):
                if event.is_channel and event.chat.id in self.id_of_urls.keys():
                    for filter in self.filters:
                        if filter.lower() in event.message.message.lower():
                            await event.message.forward_to(redirect_to)
                # await client.forward_messages(1308256189,event.message,event.message.id)
                # await client.send_message(entity=channel, message="Hello python")

            client.run_until_disconnected()

    def run(self):
        t = threading.Thread(target=self.run_tele, args=(self.loop,), daemon=True)
        t.start()
        while True:
            self.title = input('input title')


loop = asyncio.new_event_loop()
TeleParser(loop, api_id, api_hash, filter_filename, urls_filename, id_file)
