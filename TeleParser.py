import asyncio
import os
import threading
import traceback

from telethon import TelegramClient, events,sync
from telethon.tl.types import Channel


class TeleParser:
    id_of_urls = []

    def __init__(self, loop, api_id, api_hash, filters, urls, id_file, reg_phrase,logger):
        self.loop = loop
        self.bot_id = 0
        self.logger = logger
        self.api_id = api_id
        self.api_hash = api_hash
        self.filters = filters
        self.urls = urls
        self.id_file = id_file
        self.load_bot_id()

        self.redirect_to = 'me'
        self.reg_phrase = reg_phrase


        self.load_id_of_urls()
        self.run()


    def load_id_of_urls(self):
        if os.path.isfile(self.id_file):
            with open(self.id_file, encoding='utf-8') as inf:
                id_of_urls = dict()
                temp = [x.strip().split(':') for x in inf.readlines()]
                for item in temp:
                    id_of_urls[int(item[0])] = item[1]
                print(f'[PARSER] : {id_of_urls}')
                self.logger.info(f'[PARSER] : {id_of_urls}')
        else:
            with open(self.id_file, mode='w', encoding='utf-8') as ouf:
                pass
            id_of_urls = []
        self.id_of_urls = id_of_urls

    def update_urls_id(self, client):
        asd = client.get_dialogs()
        channels_list = {d.entity.id: f't.me/{d.entity.username}'
                         for d in asd
                         if d.is_channel and f't.me/{d.entity.username}' in self.urls}
        print(f'[PARSER] : {self.urls}')
        self.logger.info(f'[PARSER] : {self.urls}')
        for url in self.urls:
            if url not in channels_list.values():
                channels_list[client.get_entity(url).id] = url
        if set(channels_list) != self.id_of_urls:
            self.id_of_urls = channels_list
            self.self_save_id_urls()

    def self_save_id_urls(self):
        with open(self.id_file, mode='w', encoding='utf-8') as ouf:
            for key, value in self.id_of_urls.items():
                ouf.write(f'{key}:{value}\n')

    def save_bot_id(self, uid):
        self.bot_id = uid
        with open('bot_id', mode='w', encoding='utf-8') as ouf:
            ouf.write(str(uid))

    def load_bot_id(self):
        if os.path.isfile('bot_id'):
            with open('bot_id', mode='r', encoding='utf-8') as ouf:
                self.bot_id = int(ouf.read().strip())
        else:
            with open('bot_id', mode='w', encoding='utf-8') as ouf:
                ouf.write('0')

    def get_mode(self):
        return self.redirect_to

    def switch_mode(self, mode):
        if mode == 'me':
            self.redirect_to = 'me'
        else:
            self.redirect_to = self.bot_id

    def run_tele(self, loop):
        try:
            asyncio.set_event_loop(loop)
            with TelegramClient('name', self.api_id, self.api_hash, loop=loop) as client:
                # loading
                client.send_message('me', 'Hello, myself!')
                print(f'[PARSER] : {client.download_profile_photo("me")}')
                self.logger.info(f'[PARSER] : {client.download_profile_photo("me")}')
                client: TelegramClient
                self.update_urls_id(client)
                print(f'[PARSER] : {self.id_of_urls}')
                self.logger.info(f'[PARSER] : {self.id_of_urls}')
                ch: Channel

                # print(channels['asdasdasdas'].__dict__)

                @client.on(events.NewMessage(incoming=True))
                async def handler(event: events.newmessage.NewMessage.Event):
                    print(f'[PARSER] : {event.message}')
                    self.logger.info(f'[PARSER] : {event.message}')
                    if event.message.message == self.reg_phrase:
                        self.save_bot_id(event.message.from_id)
                    if event.is_channel and event.chat.id in self.id_of_urls.keys():
                        for filter in self.filters:
                            if filter.lower() in event.message.message.lower():
                                print(f'[PARSER] Finded message with filter {filter} : {event.message.message}')
                                await event.message.forward_to(self.redirect_to)
                                break
                    # await client.forward_messages(1308256189,event.message,event.message.id)
                    # await client.send_message(entity=channel, message="Hello python")

                client.run_until_disconnected()
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            raise Exception('PROBLEM WITH PARSER,CHECK LOG FILE')

    def run(self):
        t = threading.Thread(target=self.run_tele, args=(self.loop,), daemon=True)
        t.start()
