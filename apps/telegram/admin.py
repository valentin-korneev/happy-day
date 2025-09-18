from django.contrib import admin

from apps.telegram.models import Bot, Chat, Message


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_secure']

    def token_secure(self, obj):
        return obj.token[:10] + '...'


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_id', 'bot', 'is_default']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'chat', 'chat__bot', 'created_at']

    def text_short(self, obj):
        return obj.text[:50] + '...'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False