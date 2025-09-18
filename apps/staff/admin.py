from datetime import date

from django.contrib import admin
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse

from apps.openrouter.models import AIModel
from apps.openrouter.services import OpenRouterService
from apps.staff.forms import CongratulationParamsForm, CongratulationAIMessageForm
from apps.staff.models import Department, Position, Employee
from apps.telegram.models import Chat
from apps.telegram.services import TelegramService


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'department', 'position', 'birthday', 'is_today']
    change_list_template = 'admin/staff/employee/change_list.html'

    def is_today(self, obj):
        return obj.birthday.day == obj.birthday.today().day and obj.birthday.month == obj.birthday.today().month
    is_today.boolean = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('congratulate/', self.admin_site.admin_view(self.congratulate), name='employees_congratulate'),
        ]
        return custom_urls + urls

    def congratulate(self, request):
        step = request.GET.get('step', '1')

        if step == '1':
            if request.method == 'POST':
                form = CongratulationParamsForm(request.POST)
                if form.is_valid():
                    request.session['model_id'] = form.cleaned_data['model_id'].id
                    request.session['chat_id'] = form.cleaned_data['chat_id'].id
                    request.session['ids'] = [u.id for u in form.cleaned_data['employees']]
                    url = reverse('admin:employees_congratulate')
                    return redirect(f'{url}?step=2')
            else:
                today = date.today()
                initial_data = {
                    'employees': Employee.objects.filter(
                        birthday__day=today.day,
                        birthday__month=today.month,
                    ).all()
                }

                default_model = AIModel.objects.filter(is_default=True).first()
                if default_model:
                    initial_data['model_id'] = default_model

                default_chat = Chat.objects.filter(is_default=True).first()
                if default_chat:
                    initial_data['chat_id'] = default_chat

                form = CongratulationParamsForm(initial=initial_data)

            context = dict(
                self.admin_site.each_context(request),
                title='Поздравить сотрудников - шаг 1',
                form=form,
                step='1',
            )
            return render(request, 'admin/staff/congratulate/step1.html', context)

        elif step == '2':
            model_id = request.session['model_id']
            chat_id = request.session['chat_id']
            ids = request.session['ids']

            employees = Employee.objects.filter(id__in=ids)
            if request.method == 'POST':
                form = CongratulationAIMessageForm(request.POST)
                if form.is_valid():
                    message = form.cleaned_data['message_ai']
                    tg_service = TelegramService(Chat.objects.get(pk=chat_id))
                    tg_service.send_message(message, employees)
                    request.session['model_id'] = None
                    request.session['chat_id'] = None
                    request.session['ids'] = None
                    request.session['message_sent'] = message.splitlines()
                    url = reverse('admin:employees_congratulate')
                    return redirect(f'{url}?step=3')
            else:
                ai_service = OpenRouterService(model=AIModel.objects.get(pk=model_id))
                initial_text = ai_service.generate_birthday_message(employees)
                form = CongratulationAIMessageForm(initial={'message_ai': initial_text})

            context = dict(
                self.admin_site.each_context(request),
                title='Поздравить пользователей — шаг 2',
                form=form,
                step=2,
            )
            return render(request, "admin/staff/congratulate/step2.html", context)
        elif step == '3':
            message_lines = request.session['message_sent']
            return render(
                request,
                'admin/staff/congratulate/step3.html',
                dict(
                    self.admin_site.each_context(request),
                    title='Поздравить пользователей — шаг 3',
                    message_lines=message_lines,
                    step=3,
                )
            )
