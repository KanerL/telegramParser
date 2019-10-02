import random
import string
import time

import telebot, os
from telebot import types

from conf import *


class TGBot:

    knownUsers = set()#
    userStep = {}  # so they won't reset every time the bot restarts
    commands = {  # command description used in the "help" command
        'start': 'Начать работу с ботом',
        'help': 'Надает информацию о командах бота',
        'urls': 'Надает список каналов которые мониторятся ',
        'urls add url,url2,url3...': 'Добавляет url1,url1,url3... в список каналов для мониторинга ',
        'urls addfile': 'Добавить каналы из файла ',
        'filters': 'Надает список фильтров для отбора сообщений ',
        'filters add filter1,filter2,filter3...': 'Добавляет filter1,filter2,filter3... в список фильтров',
        'filters addfile': 'Добавить фильтры из файла ',
        'register_parser_account' : 'Регистрация парсера в боте(нужно вести код из консоли приложения)'
    }


    def __init__(self, filters, urls,reg_phrase,bot,logger):
        self.filters = filters
        self.urls = urls
        self.parser_id = 0
        self.load_parser_id()
        self.reg_phrase = reg_phrase
        self.logger = logger
        if bot is None:
            self.bot = telebot.TeleBot(API_TOKEN)
            self.server = False
        else:
            self.bot = bot
            self.server = True

    # error handling if user isn't known yet
    # (obsolete once known users are saved to file, because all users
    #   had to use the /start command and are therefore known to the bot)
    def save_known_users(self):
        self.logger.info('Starting load known users')
        with open('known_users.txt', mode='w', encoding='utf-8') as ouf:
            for item in self.knownUsers:
                ouf.write(f'{item}\n')
        self.logger.info('Loaded known users')

    def save_user_steps(self):
        self.logger.info('Starting load user steps ')
        with open('users_steps.txt', mode='w', encoding='utf-8') as ouf:
            for key, value in self.userStep.items():
                ouf.write(f'{key}:{value}\n')
        self.logger.info('Loaded user steps ')

    def save_parser_id(self, uid):
        self.parser_id = uid
        with open('parser_id', mode='w', encoding='utf-8') as ouf:
            ouf.write(str(uid))

    def load_known_users(self):
        if os.path.isfile('known_users.txt'):
            with open('known_users.txt', encoding='utf-8') as inf:
                self.knownUsers = {int(x.strip()) for x in inf.readlines()}
        else:
            with open('known_users.txt', mode='w', encoding='utf-8') as ouf:
                pass
            self.knownUsers = set()

    def load_user_steps(self):
        self.userStep = {}
        if os.path.isfile('users_steps.txt'):
            with open('users_steps.txt', encoding='utf-8') as inf:
                for line in inf.readlines():
                    item = line.strip().split(':')
                    self.userStep[int(item[0])] = int(item[1])
        else:
            with open('users_steps.txt', mode='w', encoding='utf-8') as ouf:
                pass
            self.userStep = {}

    def load_parser_id(self):
        if os.path.isfile('parser_id'):
            with open('parser_id', mode='r', encoding='utf-8') as ouf:
                self.parser_id = int(ouf.read().strip())
        else:
            with open('parser_id', mode='w', encoding='utf-8') as ouf:
                ouf.write('0')

    def get_user_step(self, uid):
        if uid in self.userStep:
            return self.userStep[uid]
        else:

            self.knownUsers.add(uid)
            self.userStep[uid] = 0
            print(f"Step : New user detected, who hasn't used \"/start\" yet {uid}")
            self.save_known_users()
            self.save_user_steps()
            return 0

    def set_user_step(self, uid, step):
        if uid in self.userStep:
            self.userStep[uid] = step
        else:

            self.knownUsers.add(uid)
            self.userStep[uid] = 0
            print("Set : New user detected, who hasn't used \"/start\" yet")
            self.save_known_users()
        self.save_user_steps()

    # only used for console output now
    def listener(self, messages):
        """
        When new messages arrive TeleBot will call this function.
        """
        for m in messages:
            if m.content_type == 'text':
                # print the sent message to the console
                print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

    def url_list_processor(self, items, action='add'):
        good_list = []
        bad_list = []
        for item in items:
            if item.startswith('t.me/') or item.startswith('t.me/joinchat/'):
                good_list.append(item)
            else:
                bad_list.append(item)
        if action == 'add':
            for item in good_list:
                self.urls.add(item)
        elif action == 'remove':
            for item in good_list:
                if item in self.urls:
                    self.urls.remove(item)
                else:
                    bad_list.append(item)
        elif action == 'removeall':
            for _ in range(len(self.urls)):
                self.urls.pop()
        with open('urls.txt', mode='w', encoding='utf-8') as ouf:
            for item in self.urls:
                ouf.write(f'{item}\n')
        return bad_list, good_list
    def filters_list_processor(self,items,action='add'):
        if action == 'add':
            for item in items:
                self.filters.add(item)
        elif action == 'remove':
            for item in items:
                if item in self.filters:
                    self.filters.remove(item)
        elif action == 'removeall':
            for _ in range(len(self.filters)):
                self.filters.pop()
        with open('filters.txt', mode='w', encoding='utf-8') as ouf:
            for item in self.filters:
                ouf.write(f'{item}\n')
        return items
    def start(self):
        self.load_known_users()
        self.load_user_steps()
        print(self.userStep)
        bot = self.bot
        bot.set_update_listener(self.listener)

        # handle the "/start" command
        @bot.message_handler(commands=['start'])
        def command_start(m: telebot.types.Message):
            cid = m.chat.id
            if cid not in self.knownUsers:  # if user hasn't used the "/start" command yet:
                self.set_user_step(cid,0)
                #bot.forward_message(self.parser_id,cid,m.message_id)
                if CUSTOM_START != '':
                    bot.send_message(cid,CUSTOM_START)
                else:
                    bot.send_message(cid, "Здраствуй ,пользователь!...")
                command_help(m)  # show the new user the help page
            else:
                bot.send_message(cid, "Ты уже пользовался этой коммандой!")
                command_help(m)  # show the new user the help page

        # help page
        @bot.message_handler(commands=['help'])
        def command_help(m: telebot.types.Message):
            cid = m.chat.id
            help_text = "Доступные команды: \n"
            for key in self.commands:  # generate help text out of the commands dictionary defined at the top
                help_text += "/" + key + ": "
                help_text += self.commands[key] + "\n"
            bot.send_message(cid, help_text)  # send the generated help page

        @bot.message_handler(commands=['urls'])
        def command_urls(m: telebot.types.Message):
            cid = m.chat.id
            text = ''
            bad_list = []
            good = []
            action = ''
            if m.text == '/urls':
                text = "Каналы которые мониторятся: \n"
                for key in self.urls:  # generate help text out of the commands dictionary defined at the top
                    text += key + "\n"
            elif m.text.startswith('/urls add '):
                action = 'add'
                item_str_list = m.text[10:]
                if ' ' in item_str_list:
                    command_default(m)
                    return
                if ',' in item_str_list:
                    bad_list, good = self.url_list_processor(item_str_list.split(','))
                else:
                    bad_list, good = self.url_list_processor([item_str_list])
            elif m.text.startswith('/urls remove '):
                action = 'remove'
                item_str_list = m.text[13:]
                if ' ' in item_str_list:
                    command_default(m)
                    return
                if ',' in item_str_list:
                    bad_list, good = self.url_list_processor(item_str_list.split(','), action='remove')
                else:
                    bad_list, good = self.url_list_processor([item_str_list], action='remove')
            elif m.text == '/urls removeall':
                self.url_list_processor([],action='removeall')
                text += 'Список каналов был успешно очищен \n'
            elif m.text == '/urls addfile':
                text += "Отправьте файл с каналами.(Каждый канал с новой строчки)"
                self.set_user_step(cid, 101)
            if good:
                if action == 'add':
                    text += 'Каналы успешно добавлены: \n'
                elif action == 'remove':
                    text += 'Каналы были успешно удалены: \n'
                text += '\n'.join(good)
            if bad_list:
                if action == 'add':
                    text += "\nКаналы не были добавлены(причинна: не отформатированы по виду t.me/link или t.me/joinchat/link) : \n"
                elif action == 'remove':
                    text += '\nКаналы не были удалены (причина : не отформатированы по виду t.me/link ,t.me/joinchat/link или отсутсвуют в списке мониторинга: \n'
                text += '\n'.join(bad_list)
            if text == '':
                command_default(m)
                return
            bot.send_message(cid, text)  # send the generated help page

        @bot.message_handler(commands=['filters'])
        def command_filters(m: telebot.types.Message):
            cid = m.chat.id
            text = ''
            good = []
            action = ''
            if m.text == '/filters':
                text = "Фильтры по отбору сообщений: \n"
                for key in self.filters:  # generate help text out of the commands dictionary defined at the top
                    text += key + "\n"
            elif m.text.startswith('/filters add '):
                action = 'add'
                item_str_list = m.text[13:]
                if ' ' in item_str_list:
                    command_default(m)
                    return
                if ',' in item_str_list:
                    good = self.filters_list_processor(item_str_list.split(','))
                else:
                    good = self.filters_list_processor([item_str_list])
            elif m.text.startswith('/filters remove '):
                action = 'remove'
                item_str_list = m.text[16:]
                if ' ' in item_str_list:
                    command_default(m)
                    return
                if ',' in item_str_list:
                    good = self.filters_list_processor(item_str_list.split(','),action=action)
                else:
                    good = self.filters_list_processor([item_str_list],action=action)
            elif m.text == '/filters removeall':
                self.filters_list_processor([],action='removeall')
                text += 'Список фильтров был успешно очищен \n'
            elif m.text == '/filters addfile':
                text += "Отправьте файл с фильтрами.(Каждый фильтр с новой строчки)"
                self.set_user_step(cid, 102)
            if good:
                if action == 'add':
                    text += 'Фильтры успешно добавлены: \n'
                elif action == 'remove':
                    text += 'Фильтры были успешно удалены: \n'
                text += '\n'.join(good)
            if text == '':
                command_default(m)
                return
            bot.send_message(cid, text)  # send the generated help page

        @bot.message_handler(commands=['register_parser_account'])
        def handle_register_parser(m: telebot.types.Message):
            cid = m.chat.id
            self.set_user_step(cid, 69)
            bot.send_message(cid, 'Введите код который написан в консоли приложения')
            global REGISTER_CODE
            REGISTER_CODE = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            print('PARSER REGISTER CODE : ' + REGISTER_CODE)

        @bot.message_handler(content_types=['document'])
        def handle_docs(m: telebot.types.Message):
            cid = m.chat.id
            status = self.get_user_step(cid)
            if status == 101 or status == 102:
                import requests
                file_info = bot.get_file(m.document.file_id)
                file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(self.TOKEN, file_info.file_path))
                if status == 101:
                    bad, good = self.url_list_processor([_.strip() for _ in file.text.split('\n')])
                    text = 'Каналы успешно добавлены: \n'
                    text += '\n'.join(good)
                    text += "\nКаналы не были добавлены(причинна не отформатированы по виду t.me/link или t.me/joinchat/link) : \n"
                    text += '\n'.join(bad)
                elif status == 102:
                    items = [_.strip() for _ in file.text.split('\n')]
                    for item in items:
                        self.filters.add(item)
                    text = 'Фильтры успешно были добавлены: \n'
                    text += '\n'.join(items)
                self.set_user_step(cid, 0)
                bot.send_message(cid, text)  # send the generated help page
            else:
                bot.send_message(cid, 'Не могу понять для чего этот файл .Попробуй ввести /help')

        @bot.message_handler(func=lambda message: self.get_user_step(message.chat.id) == 69)
        def handle_register_answer(m: telebot.types.Message):
            cid = m.chat.id
            global REGISTER_CODE
            self.set_user_step(cid, 0)
            if m.text == REGISTER_CODE:
                self.save_parser_id(cid)
                bot.send_message(cid, 'Регистрация успешна')
                bot.send_message(cid,self.reg_phrase)
            else:
                bot.send_message(cid, 'Вы ввели неправильный код,попробуйте ещё раз используя /register_parser_account')

        @bot.message_handler(func=lambda message: message.chat.id == self.parser_id)
        def handle_parsered_answer(m: telebot.types.Message):
            for user in self.knownUsers:
                 if user != self.parser_id:
                     bot.forward_message(user,m.chat.id,m.message_id)
        # default handler for every other text
        @bot.message_handler(func=lambda message: True, content_types=['text'])
        def command_default(m):
            # this is the standard reply to a normal message
            bot.send_message(m.chat.id, "Формат команды не ясен \"" + m.text + "\"\nПопробуйте ввести что-то из /help")
        if not self.server:
            bot.remove_webhook()
            bot.polling()



