import telebot
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(token)
timetable = 'Следующая лекция в сентябре!!'


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Посмотпеть расписание")
    markup.add(item1)
    item2 = types.KeyboardButton("Отправить письмо Лектору")
    markup.add(item2)
    item3 = types.KeyboardButton("Спикеры на сегодня")
    markup.add(item3)
    item4 = types.KeyboardButton("Где у Электроника кнопка?")
    markup.add(item4)

    bot.send_message(message.chat.id, 'Выберите нужный пункт меню', reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Отправить письмо Лектору":
        bot.send_message(message.chat.id, "Ури, Сегодня только фуршет!!!)))")
    if message.text == "Посмотпеть расписание":
        bot.send_message(message.chat.id, text=timetable)
    if message.text == "Спикеры на сегодня":
        bot.send_message(message.chat.id, text='Список пока не определен')
    if message.text == "Где у Электроника кнопка?":
        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        bot.send_message(message.from_user.id, text="Хочешь ссылку на фильм?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "https://www.ivi.ru/watch/priklucheniya-elektronika/6291")
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Не забудь посмотреть потом!!")


bot.infinity_polling()
