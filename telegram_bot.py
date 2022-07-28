import json
import os

import sqlite3

from datetime import datetime

from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types


def is_event_today():
    con = sqlite3.connect('tbot.sqlite3')
    cursor = con.cursor()
    today = datetime.now().strftime('%Y%m%d')
    cursor.execute('select event_id,name from events where event_date = {}'.format(today))
    cursor_data = cursor.fetchall()
    return cursor_data


NOT_FOUND_MESSAGE = 'Информация не найдена'

with open('./example.json', 'rb') as file:
    events_dict = json.load(file)

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
bot = TeleBot(token)
timetable = 'Следующая лекция в сентябре!!'


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    
    
    bot_command = types.BotCommand('start', 'Стартовая страница')
    command_scope = types.BotCommandScopeChat(message.chat.id)
    bot.set_my_commands([bot_command], command_scope)
    
    try:
        event_name = is_event_today()[0][1]
        bot.send_message(message.chat.id, 'Привет, сегодня проходит мероприятие {}'.format(event_name))
    except IndexError:
        bot.send_message(message.chat.id, 'Привет, сегодня мероприятие не проходит')

    button = types.InlineKeyboardButton('Главное меню', callback_data='menu')
    markup = types.InlineKeyboardMarkup()
    markup.add(button)
    bot.send_message(message.chat.id, reply_markup=markup, text='Привет!\nИнфо о боте')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    markup = types.InlineKeyboardMarkup()

    if call.data == "program":

        for event in events_dict:
            markup.add(
                types.InlineKeyboardButton(
                    event['name'],
                    callback_data=f'program_{event["id"]}'
                )
            )

        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='menu'))

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Программа')

    elif call.data == "menu":
        button1 = types.InlineKeyboardButton('Программа', callback_data='program')
        button2 = types.InlineKeyboardButton('Задать вопрос спикеру', callback_data='ask_speaker')

        markup.add(button1, button2)

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Главное меню')

    elif call.data == 'ask_speaker':
        for event in events_dict:
            markup.add(
                types.InlineKeyboardButton(
                    event['name'],
                    callback_data=f'ask_speaker_{event["id"]}'
                )
            )

        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='menu'))

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Задать вопрос спикеру')

    else:
        for event in events_dict:
            if call.data == f'program_{event["id"]}':
                for block in event['blocks']:
                    markup.add(
                        types.InlineKeyboardButton(
                            block['name'],
                            callback_data=f'program_{block["id"]}'
                        )
                    )

                markup.add(types.InlineKeyboardButton('Назад', callback_data='program'))
                bot.send_message(call.message.chat.id, reply_markup=markup, text=event['name'])

            elif call.data == f'ask_speaker_{event["id"]}':
                for block in event['blocks']:
                    markup.add(
                        types.InlineKeyboardButton(
                            f'{block["start_time"]} - {block["end_time"]}',
                            callback_data=f'ask_speaker_{block["id"]}'
                        )
                    )

                markup.add(types.InlineKeyboardButton('Назад', callback_data='ask_speaker'))
                bot.send_message(call.message.chat.id, reply_markup=markup, text=event['name'])

            for block in event['blocks']:
                if call.data == f'program_{block["id"]}':
                    markup.add(types.InlineKeyboardButton('Назад', callback_data=f'program_{event["id"]}'))
                    text = block.get('text') or NOT_FOUND_MESSAGE
                    bot.send_message(call.message.chat.id, reply_markup=markup, text=text)

                elif call.data == f'ask_speaker_{block["id"]}':
                    for speaker in block['speakers']:
                        markup.add(
                            types.InlineKeyboardButton(
                                f'{speaker["speaker_id"]} - {speaker["name"]}',
                                callback_data=speaker["id"]
                            )
                        )

                    markup.add(types.InlineKeyboardButton('Назад', callback_data=f'ask_speaker_{event["id"]}'))
                    bot.send_message(
                        call.message.chat.id,
                        reply_markup=markup,
                        text=f'{block["start_time"]} - {block["end_time"]}'
                    )

                if block['speakers']:
                    for speaker in block['speakers']:
                        if call.data == speaker['id']:
                            speaker_answer = bot.send_message(call.message.chat.id, text='Введите вопрос докладчику:')
                            bot.register_next_step_handler(speaker_answer, send_message_to_speaker, speaker['speaker_id'])



def send_message_to_speaker(message, chat_id):
    bot.send_message(chat_id, message.text)


bot.infinity_polling()
