from django.contrib import admin
from django.template.response import TemplateResponse
from apps.staff.models import Employee


def custom_index(self, request, extra_context=None):
    context = {
        **self.each_context(request),
        'title': 'Администрирование',
        'app_list': self.get_app_list(request),
        **(extra_context or {}),
        'happy_staff': Employee.birthday_staff.all()
    }
    return TemplateResponse(request, 'admin/index.html', context)


admin.site.index = custom_index.__get__(admin.site, admin.AdminSite)
admin.site.site_header = 'Альфа-поздравление'
admin.site.site_url = None