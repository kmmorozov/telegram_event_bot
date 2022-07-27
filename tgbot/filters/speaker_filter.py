from telebot.custom_filters import SimpleCustomFilter
from tgbot.models.users_model import Speaker


class SpeakerFilter(SimpleCustomFilter):
    """
    Filter for speakers
    """

    key = 'speaker'

    def check(self, message):

        return int(message.chat.id) == int(Speaker.SPEAKER.value)
    # TODO Запрос к базе и проверка на принадлежность к докладчику
