import csv
import os
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from apps.openrouter.models import Service
from apps.openrouter.services import OpenRouterService
from apps.staff.forms import (
    CongratulationBirthdayForm,
    CongratulationHolidayForm,
    CongratulationMessageForm,
)
from apps.staff.models import Department, Position, Employee
from apps.staff.parse_date import parse_date
from apps.telegram.models import Publisher
from apps.telegram.services import TelegramService
from config import settings


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'department', 'position', 'is_birthday_today']
    change_list_template = 'admin/staff/employee/change_list.html'

    def is_birthday_today(self, obj):
        return obj.birthday.day == obj.birthday.today().day and obj.birthday.month == obj.birthday.today().month

    is_birthday_today.boolean = True
    is_birthday_today.short_description = 'День рождения сегодня'


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('congratulate/birthday', self.admin_site.admin_view(self.congratulate_birthday), name='congratulate_birthday'),
            path('congratulate/holiday', self.admin_site.admin_view(self.congratulate_holiday), name='congratulate_holiday'),
            path('upload-employees/', self.upload_employees, name='upload_employees'),
        ]
        return custom_urls + urls

    def congratulate(self, request, is_birthday=False):
        step = int(request.GET.get('step', '1'))
        url_name = f'admin:{"congratulate_birthday" if is_birthday else "congratulate_holiday"}'
        title = f'Поздравление сотрудников{" с Днем Рождения" if is_birthday else ""} - шаг {step}'

        if step == 1:
            form_class = CongratulationBirthdayForm if is_birthday else CongratulationHolidayForm
            if request.method == 'POST':
                form = form_class(request.POST)
                if form.is_valid():
                    request.session['publisher'] = form.cleaned_data['publisher'].id
                    extra_info = []

                    if is_birthday:
                        request.session['employees'] = [e.id for e in form.cleaned_data['employees']]
                        employees = form.cleaned_data['employees']

                        for employee in employees:
                            employee_info = employee.full_name
                            if employee.telegram_id:
                                employee_info = f'<a href="https://t.me/{employee.telegram_id}">{employee_info}</a>'
                            employee_info = f' - {employee_info}'
                            work_info = []
                            if employee.department:
                                work_info.append(employee.department.name)
                            if employee.position:
                                work_info.append(employee.position.name)
                            if work_info:
                                employee_info += f' ({", ".join(work_info)})'
                            extra_info.append(employee_info)
                    else:
                        extra_info = form.cleaned_data['reason'].splitlines()

                    try:
                        service = OpenRouterService(service=form.cleaned_data['service'])
                        request.session['message'] = service.generate_message(extra_info='\n'.join(extra_info))
                    except Exception as e:
                        form.add_error(None, str(e))
                    else:
                        return redirect(f'{reverse(url_name)}?step=2')
            else:
                initial_data = {}

                if is_birthday:
                    initial_data['employees'] = Employee.birthday_staff.birthday()

                default_service = Service.objects.filter(is_default=True).first()
                if default_service:
                    initial_data['service'] = default_service

                default_publisher = Publisher.objects.filter(is_default=True).first()
                if default_publisher:
                    initial_data['publisher'] = default_publisher

                form = form_class(initial=initial_data)

            context = dict(
                self.admin_site.each_context(request),
                title=title,
                form=form,
                step=1,
            )
            return render(request, 'admin/staff/congratulate/step1.html', context)

        elif step == 2:
            message = request.session['message']
            publisher_id = request.session['publisher']

            if request.method == 'POST':
                form = CongratulationMessageForm(request.POST)
                if form.is_valid():
                    message = form.cleaned_data['message']

                    images = []
                    if is_birthday:
                        staff_ids = request.session['employees']
                        employees = Employee.objects.filter(id__in=staff_ids)

                        for employee in employees:
                            if employee.image:
                                relative_path = employee.image.url.replace('/media/', '')
                                images.append(os.path.join(settings.MEDIA_ROOT, relative_path))

                    try:
                        tg_service = TelegramService(Publisher.objects.get(id=publisher_id))
                        tg_service.send_message(message, images=images)
                    except Exception as e:
                        form.add_error(None, str(e))
                    else:
                        request.session['publisher_id'] = None
                        request.session['employees'] = None
                        request.session['message'] = message

                        url = reverse(url_name)
                        return redirect(f'{url}?step=3')
            else:
                form = CongratulationMessageForm(initial={'message': message})


            context = dict(
                self.admin_site.each_context(request),
                title=title,
                form=form,
                step=2,
            )
            return render(request, "admin/staff/congratulate/step2.html", context)

        message_lines = request.session['message'].splitlines()
        return render(
            request,
            'admin/staff/congratulate/step3.html',
            dict(
                self.admin_site.each_context(request),
                title=title,
                message_lines=message_lines,
                step=3,
            )
        )

    def congratulate_birthday(self, request):
        return self.congratulate(request, is_birthday=True)

    def congratulate_holiday(self, request):
        return self.congratulate(request)

    def upload_employees(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, 'Файл не выбран')
                return HttpResponseRedirect('../')

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Неверный формат файла')
                return HttpResponseRedirect('../')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)

                next(reader, None)

                for row in reader:
                    if len(row) >= 4 and row[0]:
                        try:
                            full_name = row[0].split(' ')
                            if len(full_name) < 2:
                                raise ValueError('ФИО должно состоять хотя бы из Фамилии и имени')
                            last_name = full_name[0]
                            first_name = full_name[1]
                            middle_name = ''
                            if len(full_name) > 2:
                                middle_name = ' '.join(full_name[2:])

                            emp = Employee.objects.filter(
                                first_name=first_name,
                                last_name=last_name,
                                middle_name=middle_name,
                                birthday=parse_date(row[3].lower()),
                            ).first()

                            if emp is None:
                                emp = Employee.objects.create(
                                    first_name=first_name,
                                    last_name=last_name,
                                    middle_name=middle_name,
                                    birthday=parse_date(row[3].lower()),
                                )
                            else:
                                messages.success(
                                    request,
                                    f'Пользователь {emp.full_name} уже существует - '
                                    f'обновлена информация о должности и подразделении'
                                )

                            position_name = row[1]
                            if position_name:
                                emp.position = Position.objects.get_or_create(name=position_name)[0]

                            department_name = row[2]
                            if department_name:
                                emp.department = Department.objects.get_or_create(name=department_name)[0]

                            emp.save()
                        except Exception as e:
                            print(e)
                            messages.error(request, str(e))

                messages.success(request, 'Файл успешно загружен')
            except Exception as e:
                messages.error(request, f'Ошибка при обработке файла: {str(e)}')

            return HttpResponseRedirect('../')

        context = dict(
            self.admin_site.each_context(request),
            title='Загрузка сотрудников',
            step=1,
        )

        return render(request, 'admin/staff/csv_upload_form.html', context)