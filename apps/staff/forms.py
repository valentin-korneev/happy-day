from django import forms
from apps.openrouter.models import Service
from apps.staff.models import Employee
from apps.telegram.models import Publisher


class CongratulationBirthdayForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label='Сервис генерации текста',
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        label='Отправитель',
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.birthday_staff.none(),
        label='Сотрудники',
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employees'].queryset = Employee.birthday_staff.birthday()


class CongratulationHolidayForm(forms.Form):
    reason = forms.CharField(
        label='Повод для поздравления'
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label='Сервис генерации текста',
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        label='Отправитель',
    )


class CongratulationMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea,
        label='Сообщение',
    )
