from telebot import TeleBot
from telebot import types
from tgbot.handlers.bot_commands import speaker_commands

def start_command(message: types.Message, bot: TeleBot):
    """
    You can create a function and use parameter pass_bot.
    """
    commands = []

    for command, description in speaker_commands.items():
        commands.append(types.BotCommand(command, description))

    command_scope = types.BotCommandScopeChat(message.chat.id)

    bot.set_my_commands(commands, command_scope)


def event(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event')


def event_program(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'event_program')


def ask_speaker(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'ask_speaker')


def answer_question(message: types.Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'answer_question')
