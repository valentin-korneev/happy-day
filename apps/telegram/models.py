from django.db import models


class Bot(models.Model):
    name = models.CharField('Наименование', max_length=255)
    token = models.CharField('Токен', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боты'


class Chat(models.Model):
    name = models.CharField('Наименование', max_length=255)
    chat_id = models.CharField('Идентификатор чата', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Чаты'
        verbose_name_plural = 'Чаты'


class Publisher(models.Model):
    name = models.CharField('Наименование', max_length=255)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, verbose_name='Бот')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name='Чат')
    is_default = models.BooleanField('Используется по-умолчанию', default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            Publisher.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        unique_together= [['chat', 'bot']]
        verbose_name = 'Отправитель'
        verbose_name_plural = 'Отправители'


class Message(models.Model):
    text = models.TextField('Текст сообщения')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, verbose_name='Отправитель')
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)

    def __str__(self):
        return f'{self.text[:32]}...'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
