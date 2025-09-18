from datetime import date

from django.db import models
from django.db.models import Manager
from django.urls import reverse


class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class BirthdayManager(models.Manager):
    def get_queryset(self):
        today = date.today()
        return super().get_queryset().filter(birthday__day=today.day, birthday__month=today.month)


class Employee(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    birthday = models.DateField()
    image = models.ImageField(upload_to='images/', blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    objects = models.Manager()
    birthday_staff = BirthdayManager()

    def get_admin_url(self):
        return reverse(
            f'admin:{self._meta.app_label}_{self._meta.model_name}_change',
            args=[self.pk],
        )
