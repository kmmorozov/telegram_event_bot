import json
import os
import re
from telebot.types import LabeledPrice, ShippingOption
from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types
from telebot.apihelper import ApiTelegramException

provider_token = '1832575495:TEST:01cba465218af40acc25feac199f050b537560e46d82096d28b94a376120ad8c'
NOT_FOUND_MESSAGE = 'Информация не найдена'

with open('./example.json', 'rb') as file:
    events_dict = json.load(file)

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
bot = TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot_command = types.BotCommand('start', 'Стартовая страница')
    command_scope = types.BotCommandScopeChat(message.chat.id)
    bot.set_my_commands([bot_command], command_scope)

    button = types.InlineKeyboardButton('Главное меню', callback_data='menu')
    markup = types.InlineKeyboardMarkup()
    markup.add(button)
    bot.send_message(message.chat.id, reply_markup=markup, text='Привет!\nБот упростит навигацию по мероприятию')


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
        button3 = types.InlineKeyboardButton('Задать вопрос спикеру', callback_data='ask_speaker')
        button2 = types.InlineKeyboardButton('Отправить донат', callback_data='donate')
        markup.add(button1, button2, button3, row_width=2)

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

    elif call.data == 'donate':
        # button1 = types.InlineKeyboardButton('100', callback_data='100')
        # button3 = types.InlineKeyboardButton('500', callback_data='500')
        # button2 = types.InlineKeyboardButton('1000', callback_data='1000')
        # button4 = types.InlineKeyboardButton('10000', callback_data='10000')
        # button5 = types.InlineKeyboardButton('Вернуться в главное меню', callback_data='menu')
        # markup.add(button1, button2, button3, button4, button5, row_width=2)
        # bot.send_message(call.message.chat.id, reply_markup=markup, text='На какую суммубудет донат?')
        # print(call.message.chat.id)
        prices = [LabeledPrice(label='На развитие', amount=5678990)]
        bot.send_invoice(
            call.message.chat.id,  # chat_id
            'На развитие бота',  # title
            'Вы донатите на развитие нашего бота и нашего бесплатного MeetUP',
            'HAPPY FRIDAYS COUPON',  # invoice_payload
            provider_token,  # provider_token
            'rub',
            prices,
            is_flexible=False,
            start_parameter='time-machine-example')

        @bot.pre_checkout_query_handler(func=lambda query: True)
        def checkout(pre_checkout_query):
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                          error_message="Попробуйте еще раз оплатить через несколько минут.")

        @bot.message_handler(content_types=['successful_payment'])
        def got_payment(message):
            bot.send_message(message.chat.id,
                             'Спасибо за ваш донат! Ваше пожертвование в размере `{} {}` пойдет на добрые дела! '
                             .format(
                                 message.successful_payment.total_amount / 100, message.successful_payment.currency),
                             parse_mode='Markdown')

        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='menu'))

        bot.send_message(call.message.chat.id, reply_markup=markup, text='Или вернуться в главное меню.')
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
                                f'{speaker["name"]}',
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

    if rexp := re.search(r'^id_(\d+)$', call.data):
        answer_to_user = bot.send_message(call.message.chat.id, text='Введите ответ пользователю:')
        # print(answer_to_user)
        # print(confirm_send_message())
        # print(rexp.group(1))
        bot.register_next_step_handler(answer_to_user, confirm_send_message_user, rexp.group(1))


def confirm_send_message(message: types.Message, speaker_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Да')
    button2 = types.KeyboardButton('Нет')
    markup.add(button1, button2)

    confirmation = bot.send_message(message.chat.id, text='Отправить сообщение?', reply_markup=markup)
    bot.register_next_step_handler(confirmation, send_message_to_speaker, message, speaker_id)


def confirm_send_message_user(message: types.Message, speaker_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Да')
    button2 = types.KeyboardButton('Нет')
    markup.add(button1, button2)

    confirmation = bot.send_message(message.chat.id, text='Отправить сообщение?', reply_markup=markup)
    bot.register_next_step_handler(confirmation, send_message_to_user, message, speaker_id)


def send_message_to_speaker(message, answer, chat_id):
    if message.text == 'Да':
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'id_{message.chat.id}'))

            bot.send_message(
                chat_id,
                answer.text,
                reply_markup=markup
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


def send_message_to_user(message, answer, chat_id):
    if message.text == 'Да':
        try:
            markup = types.InlineKeyboardMarkup()
            # markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'id_{message.chat.id}'))

            bot.send_message(
                chat_id,
                answer.text,
                reply_markup=markup
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
