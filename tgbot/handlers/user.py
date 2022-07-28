from telebot import TeleBot
from telebot import types
from tgbot.handlers.bot_commands import user_commands


def start_command(message: types.Message, bot: TeleBot):
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


