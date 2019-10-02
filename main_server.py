import asyncio
import os
import random
import string

from TeleParser import TeleParser
from statbot import TGBot
import time
import flask
import telebot
urls_filename = 'urls.txt'
filters_filename = 'filters.txt'
api_id = 1103463
api_hash = '91971674d49ac402c515c2a85957c032'
id_file = 'id_file.txt'
REGISTER_CODE = ''
REGISTER_PHRASE = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
API_TOKEN = '857758104:AAGTqSjB9tQRMMUkZlJChQLH57ExRRAUKYA'

WEBHOOK_HOST = '18.216.72.123'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

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

bot.remove_webhook()
time.sleep(1)
print(WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
                 certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server

loop = asyncio.new_event_loop()
filters = load_filters(filters_filename)
users = load_urls(urls_filename)
tp = TeleParser(loop, api_id, api_hash, filters, users, id_file,REGISTER_PHRASE)
tp.switch_mode('bot')
TGBot(filters,users,REGISTER_PHRASE,bot = bot).start()
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)