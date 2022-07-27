from telebot import TeleBot
from telebot import types
from tgbot.handlers.bot_commands import user_commands


def start_command(message: types.Message, bot: TeleBot):
    # item1 = types.InlineKeyboardButton("Описание события", callback_data='event')
    # item2 = types.InlineKeyboardButton("Задать вопрос докладчику", callback_data='ask_speaker')
    # item3 = types.InlineKeyboardButton("Программа мероприятия", callback_data='event_program')
    #
    # keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(item1)
    # keyboard.add(item2)
    # keyboard.add(item3)
    # bot.send_message(message.chat.id, text='Пользователь', reply_markup=keyboard)
    # bot.send_message(message.chat.id, "Event info")
    commands = []

    for command, description in user_commands.items():
        commands.append(types.BotCommand(command, description))

    command_scope = types.BotCommandScopeChat(message.chat.id)

    bot.set_my_commands(commands, command_scope)


def event(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event')


def event_program(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event_program')


def ask_speaker(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'ask_speaker')


