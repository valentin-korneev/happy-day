from datetime import date

from django import forms
from apps.openrouter.models import AIModel
from apps.staff.models import Employee
from apps.telegram.models import Chat


class CongratulationParamsForm(forms.Form):
    model_id = forms.ModelChoiceField(
        queryset=AIModel.objects.all(),
        label='AI-модель для генерации поздравления',
    )
    chat_id = forms.ModelChoiceField(
        queryset=Chat.objects.all(),
        label='Чат',
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.birthday_staff.all(),
        label='Сотрудники',
        widget=forms.CheckboxSelectMultiple,
    )


class CongratulationAIMessageForm(forms.Form):
    message_ai = forms.CharField(
        widget=forms.Textarea,
        label='Сообщение',
    )