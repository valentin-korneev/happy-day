import os

from telebot import TeleBot
from telebot.types import InputMediaPhoto

from apps.telegram.models import Message
from config import settings


class TelegramService:
    def __init__(self, chat):
        self.chat = chat
        self.bot_token = self.chat.bot.token
        self.bot = TeleBot(token=self.bot_token)

    def send_message(self, message, employees):
        try:
            images = []

            for employee in employees:
                if employee.image and employee.image.url:
                    relative_path = employee.image.url.replace('/media/', '')
                    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    if images:
                        images.append(InputMediaPhoto(open(full_path, 'rb')))
                    else:
                        images.append(InputMediaPhoto(open(full_path, 'rb'), caption=message))

            if images:
                self.bot.send_media_group(
                    chat_id=self.chat.chat_id,
                    media=images,
                )
            else:
                self.bot.send_message(
                    chat_id=self.chat.chat_id,
                    text=message,
                )

            message_obj = Message.objects.create(
                text=message,
                chat=self.chat,
            )
            message_obj.employees.set(employees)

        except Exception as e:
            raise Exception(f"Ошибка при отправке в Telegram: {e}")
