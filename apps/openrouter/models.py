from django.db import models


class APIKey(models.Model):
    name = models.CharField('Наименование', max_length=255)
    value = models.CharField('Значение', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ключ API'
        verbose_name_plural = 'Ключи API'


class Provider(models.Model):
    name = models.CharField('Наименование', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class LLModel(models.Model):
    name = models.CharField('Наименование', max_length=255)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, verbose_name='Поставщик')
    model = models.CharField('Модель', max_length=255)
    is_free = models.BooleanField('Токены не монетизируются', default=False)

    def __str__(self):
        return self.name

    def get_model_id(self):
        return f'{self.provider.name}/{self.model}' + (':free' if self.is_free else '')

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'


class Service(models.Model):
    name = models.CharField('Наименование', max_length=255)
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, verbose_name='Ключ API')
    model = models.ForeignKey(LLModel, on_delete=models.CASCADE, verbose_name='Модель')
    prompt = models.TextField('Промпт')
    is_default = models.BooleanField('Используется по-умолчанию', default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            Service.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Сервис'
        verbose_name_plural = 'Сервисы'


class Message(models.Model):
    text = models.TextField('Текст сообщения')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Сервис')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f'{self.text[:32]}...'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
