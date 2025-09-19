from django.contrib import admin
from apps.openrouter.models import APIKey, Provider, LLModel, Service, Message


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'value_secure']

    def get_exclude(self, request, obj=None):
        return ['value'] if obj else []

    def get_readonly_fields(self, request, obj=None):
        return ['value_secure'] if obj else []

    def value_secure(self, obj):
        return f'{obj.value[:16]} **** {obj.value[-4:]}'

    value_secure.short_description = 'Ключ API'

    def has_change_permission(self, request, obj = ...):
        return False

    def has_delete_permission(self, request, obj = ...):
        return False


class LLModelInline(admin.TabularInline):
    model = LLModel
    can_delete = False
    extra = 0


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [LLModelInline]

    def has_delete_permission(self, request, obj = ...):
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_key', 'model', 'is_default']

    def has_delete_permission(self, request, obj = ...):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'service', 'created_at']

    def text_short(self, obj):
        return f'{obj.text[:32]} ...'

    text_short.short_description = 'Сообщение'

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]
