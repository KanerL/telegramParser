import asyncio
import os
import random
import string

from TeleParser import TeleParser
from statbot import TGBot
import time
import flask
import telebot
from conf import *
bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)


def load_filters(filter_file):
    if os.path.isfile(filter_file):
        with open(filter_file, encoding='utf-8') as inf:
            filters = [x.strip() for x in inf.readlines()]
    else:
        with open(filter_file, mode='w', encoding='utf-8') as ouf:
            pass
        filters = []
    return set(filters)


def load_urls(urls_file):
    if os.path.isfile(urls_file):
        with open(urls_file, encoding='utf-8') as inf:
            urls = []
            for x in inf.readlines():
                if x.startswith('t.me/') or x.startswith('t.me/joinchat/'):
                    urls.append(x.strip())
                else:
                    raise ValueError(f'{x} не отформатирована по виду t.me/link или t.me/joinchat/link')
    else:
        with open(urls_file, mode='w', encoding='utf-8') as ouf:
            pass
        urls = []
    return set(urls)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


bot.remove_webhook()
time.sleep(1)
print(WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
loop = asyncio.new_event_loop()
filters = load_filters(filters_filename)
users = load_urls(urls_filename)
tp = TeleParser(loop, api_id, api_hash, filters, users, id_file, REGISTER_PHRASE)
tp.switch_mode('bot')
tbot = TGBot(filters, users, REGISTER_PHRASE, bot=bot)
tbot.start()
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
