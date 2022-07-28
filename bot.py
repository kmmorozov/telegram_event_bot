# filters
from tgbot.filters.admin_filter import AdminFilter
from tgbot.filters.speaker_filter import SpeakerFilter

# handlers
from tgbot.handlers import admin
from tgbot.handlers.spam_command import anti_spam
from tgbot.handlers import user
from tgbot.handlers import speaker

# user-specific commands
from tgbot.handlers.bot_commands import user_commands
from tgbot.handlers.bot_commands import speaker_commands
from tgbot.handlers.bot_commands import admin_commands

# middlewares
from tgbot.middlewares.antiflood_middleware import antispam_func

# states
# from tgbot.states.register_state import Register
# TODO Посмотреть - нужно ли оно?

# utils
# from tgbot.utils.database import Database
# TODO Добавление базы

# telebot
from telebot import TeleBot

# config
from tgbot import config

# db = Database()

# remove this if you won't use middlewares:
from telebot import apihelper
apihelper.ENABLE_MIDDLEWARE = True

# I recommend increasing num_threads
bot = TeleBot(config.TOKEN, num_threads=5)


def register_handlers():
    bot.register_message_handler(admin.start_command, commands=['start'], admin=True, pass_bot=True)
    bot.register_message_handler(speaker.start_command, commands=['start'], speaker=True, pass_bot=True)
    bot.register_message_handler(user.start_command, commands=['start'], speaker=False, admin=False, pass_bot=True)

    bot.register_message_handler(anti_spam, commands=['spam'], pass_bot=True)

    for speaker_command in speaker_commands.keys():
        bot.register_message_handler(getattr(speaker, speaker_command), commands=[speaker_command], speaker=True,
                                     pass_bot=True)

    for user_command in user_commands.keys():
        bot.register_message_handler(getattr(user, user_command), commands=[user_command], speaker=False, admin=False,
                                                         pass_bot=True)

    for admin_command in admin_commands.keys():
        bot.register_message_handler(getattr(admin, admin_command), commands=[admin_command], admin=True,
                                     pass_bot=True)


register_handlers()

# Middlewares
bot.register_middleware_handler(antispam_func, update_types=['message'])
# TODO Доделать антиспам проверку (как фича, если будет время)

# custom filters
bot.add_custom_filter(AdminFilter())
bot.add_custom_filter(SpeakerFilter())


def run():
    bot.infinity_polling()

run()
