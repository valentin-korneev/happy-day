from django.contrib import admin

from apps.telegram.models import Bot, Chat, Publisher, Message


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_secure']

    def get_exclude(self, request, obj=None):
        return ['token'] if obj else []

    def get_readonly_fields(self, request, obj=None):
        return ['token_secure'] if obj else []

    def token_secure(self, obj):
        return f'{obj.token[:16]} **** {obj.token[-4:]}'

    token_secure.short_description = 'Токен'

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_id']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'bot', 'chat', 'is_default']

    def has_delete_permission(self, request, obj = ...):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'publisher', 'created_at']

    def text_short(self, obj):
        return f'{obj.text[:32]} ...'

    text_short.short_description = 'Сообщение'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False