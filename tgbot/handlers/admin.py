from telebot import TeleBot
from telebot import types
from tgbot.handlers.bot_commands import admin_commands


def start_command(message: types.Message, bot: TeleBot):
    """
    You can create a function and use parameter pass_bot.
    """
    commands = []

    for command, description in admin_commands.items():
        commands.append(types.BotCommand(command, description))

    command_scope = types.BotCommandScopeChat(message.chat.id)

    bot.set_my_commands(commands, command_scope)


def event(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event')
    # TODO Добавление вывода информации о событии


def event_program(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event_program')
    # TODO Добавление вывода программы, сама логика программы


def ask_speaker(message: types.Message, bot: TeleBot):
    msg = bot.send_message(message.chat.id, 'Добавить организатора:')
    bot.register_next_step_handler(msg, add_speaker_to_db, bot)


def answer_question(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'answer_question')


def add_speaker(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'add_speaker')


def add_admin(message: types.Message, bot: TeleBot):
    msg = bot.send_message(message.chat.id, 'Добавить организатора:')
    bot.register_next_step_handler(msg, add_admin_to_db, bot)


def add_admin_to_db(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, message.text)
    # TODO Верификация и добавление организатора в базу


def add_speaker_to_db(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, message.text)
    # TODO Верификация и добавление докладчика в базу
