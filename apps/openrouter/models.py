from django.db import models


class Token(models.Model):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Токен'
        verbose_name_plural = 'Токены'


class AIModel(models.Model):
    name = models.CharField(max_length=255)
    model_id = models.CharField(max_length=255)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            AIModel.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = [['model_id', 'token']]
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Message(models.Model):
    text = models.TextField()
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    employees = models.ManyToManyField('staff.Employee', related_name='ai_messages')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50] + '...'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
