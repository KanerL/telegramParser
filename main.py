#!/usr/bin/env python
# coding: utf8

import asyncio
import logging
import traceback
from logging.handlers import RotatingFileHandler

from telebot import apihelper

from TeleParser import TeleParser
from statbot import TGBot

from conf import *


def load_filters(filter_file):

    if os.path.isfile(filter_file):
        with open(filter_file, encoding='utf-8') as inf:
            filters = [x.strip() for x in inf.readlines()]
    else:
        with open(filter_file, mode='w', encoding='utf-8') as ouf:
            pass
        filters = []
    logger.info('Filters loaded' + str(filters))
    return set(filters)


def load_urls(urls_file):
    if os.path.isfile(urls_file):
        with open(urls_file, encoding='utf-8') as inf:
            urls = []
            for x in inf.readlines():
                if x.startswith('t.me/') or x.startswith('t.me/joinchat/'):
                    urls.append(x.strip())
                else:
                    raise ValueError('%s not formated in this way t.me/link ,t.me/joinchat/link' % x)
    else:
        with open(urls_file, mode='w', encoding='utf-8') as ouf:
            pass
        urls = []
    logger.info('Urls loaded' + str(urls))
    return set(urls)


logger = logging.getLogger("Rotating Log")
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler("log.txt", maxBytes=10000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
loop = asyncio.new_event_loop()
filters = load_filters(filters_filename)
users = load_urls(urls_filename)
tp = TeleParser(loop, api_id, api_hash, filters, users, id_file, REGISTER_PHRASE,logger)
tp.switch_mode('bot')
if PROXY_TYPE:
    apihelper.proxy = {PROXY_TYPE:proxyl}
try:
    tg = TGBot(filters, users, REGISTER_PHRASE,logger=logger, bot=None).start()
except Exception as e:
    logger.error(str(e))
    logger.error(traceback.format_exc())
    print('PROBLEM WITH TELEGRAM BOT,CHECK LOG FILE')
    input()
    raise Exception()
