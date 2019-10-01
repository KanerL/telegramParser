import asyncio

from telethon import TelegramClient, events, sync

api_id = 1160324
api_hash = '28e9eb2962d8d5cecb204901e53c5348'


def main():
    with TelegramClient('name', api_id, api_hash) as client:
        client.send_message('me', 'Hello, myself!')
        print(client.download_profile_photo('me'))
        client : TelegramClient
        asd = client.get_dialogs()
        for item in asd:
            print(item)

        @client.on(events.NewMessage())
        async def handler(event : events.newmessage.NewMessage.Event):
            print(event.message)
            print(event.message.id)
            channel = await  client.get_entity(1308256189)
            await event.message.forward_to(channel)
            #await client.forward_messages(1308256189,event.message,event.message.id)
            #await client.send_message(entity=channel, message="Hello python")

        client.run_until_disconnected()
    print('asdas')
asyncio.run(main())