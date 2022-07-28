import json
import os

from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types
from telebot.apihelper import ApiTelegramException


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
                            speaker_answer = bot.send_message(call.message.chat.id, text='Введите вопрос спикеру:')
                            bot.register_next_step_handler(speaker_answer, confirm_send_message, speaker['speaker_id'])


def confirm_send_message(message: types.Message, speaker_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Да')
    button2 = types.KeyboardButton('Нет')
    markup.add(button1, button2)

    confirmation = bot.send_message(message.chat.id, text='Отправить сообщение?', reply_markup=markup)
    bot.register_next_step_handler(confirmation, send_message_to_speaker, message, speaker_id)


def send_message_to_speaker(message, answer, chat_id):
    if message.text == 'Да':
        try:
            bot.send_message(
                chat_id,
                f'From: @{answer.from_user.username}\n{answer.text}'
            )
            bot.send_message(
                message.chat.id,
                'Сообщение отправлено',
                reply_markup=types.ReplyKeyboardRemove()
            )
        except ApiTelegramException:
            bot.send_message(
                message.chat.id,
                'Ошибка сервера. \nПожалуйста, повторите позднее.',
                reply_markup=types.ReplyKeyboardRemove()
            )

    elif message.text == 'Нет':
        bot.send_message(
            message.chat.id,
            'Сообщение не отправлено',
            reply_markup=types.ReplyKeyboardRemove()
        )


bot.infinity_polling()
