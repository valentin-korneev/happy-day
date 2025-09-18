from django.db import models


class Bot(models.Model):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боты'


class Chat(models.Model):
    name = models.CharField(max_length=255)
    chat_id = models.CharField(max_length=255)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.bot.name})'

    def save(self, *args, **kwargs):
        if self.is_default:
            Chat.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        unique_together= [['chat_id', 'bot']]
        verbose_name = 'Чаты'
        verbose_name_plural = 'Чаты'


class Message(models.Model):
    text = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    employees = models.ManyToManyField('staff.Employee', related_name='tg_messages')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50] + '...'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
