import json
import os


from collections import deque

from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types


NOT_FOUND_MESSAGE = 'Информация не найдена'

with open('./example.json', 'rb') as file:
    events_dict = json.load(file)

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
bot = TeleBot(token)
timetable = 'Следующая лекция в сентябре!!'

delete_message_query = deque()


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    user_name = message.from_user.username

    bot_command = types.BotCommand('start', 'Стартовая страница')
    command_scope = types.BotCommandScopeChat(message.chat.id)
    bot.set_my_commands([bot_command], command_scope)

    button = types.InlineKeyboardButton('Главное меню', callback_data='menu')
    markup = types.InlineKeyboardMarkup()
    markup.add(button)
    bot.send_message(message.chat.id, reply_markup=markup, text='Привет!\nИнфо о боте')
    delete_message_query.append(message.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    markup = types.InlineKeyboardMarkup()

    if call.data == "program":

        for event in events_dict:
            markup.add(types.InlineKeyboardButton(event['name'], callback_data=event['id']))
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='menu'))

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Программа')

    elif call.data == "menu":
        button1 = types.InlineKeyboardButton('Программа', callback_data='program')
        button2 = types.InlineKeyboardButton('Задать вопрос спикеру', callback_data='ask_speaker')

        markup.add(button1, button2)

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Главное меню')

    for event in events_dict:
        if call.data == event['id']:
            for block in event['blocks']:
                markup.add(types.InlineKeyboardButton(block['name'], callback_data=block['id']))
            markup.add(types.InlineKeyboardButton('Назад', callback_data='program'))
            bot.send_message(call.message.chat.id, reply_markup=markup, text=event['name'])

        for block in event['blocks']:
            if call.data == block['id']:
                markup.add(types.InlineKeyboardButton('Назад', callback_data=event['id']))
                text = block.get('text') or NOT_FOUND_MESSAGE
                bot.send_message(call.message.chat.id, reply_markup=markup, text=text)

    delete_message_query.append(call.message.id)

    while len(delete_message_query) > 0:
        delete = delete_message_query.popleft()
        bot.delete_message(call.message.chat.id, delete)


bot.infinity_polling()
