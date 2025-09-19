import os
from telebot import TeleBot
from telebot.types import InputMediaPhoto
from apps.telegram.models import Message


class TelegramService:
    def __init__(self, publisher):
        self.publisher = publisher
        self.bot = TeleBot(token=publisher.bot.token)
        self.chat_id = publisher.chat.chat_id

    def send_message(self, text, images=None):
        try:
            media = []

            for image in images:
                if media:
                    media.append(InputMediaPhoto(open(image, 'rb')))
                else:
                    media.append(InputMediaPhoto(open(image, 'rb'), caption=text, parse_mode='HTML'))

            if media:
                self.bot.send_media_group(
                    chat_id=self.chat_id,
                    media=media,
                )
            else:
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                )

            Message.objects.create(
                text=text,
                publisher=self.publisher,
            )
        except Exception as e:
            raise Exception(f'Ошибка при отправке в Telegram: {e}')
