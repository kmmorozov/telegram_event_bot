from telebot.custom_filters import SimpleCustomFilter
from tgbot.models.users_model import Admin


class AdminFilter(SimpleCustomFilter):
    """
    Filter for admin users
    """

    key = 'admin'

    def check(self, message):

        return int(message.chat.id) == int(Admin.ADMIN.value)
    # TODO Запрос к базе и проверка на принадлежность к организатору
