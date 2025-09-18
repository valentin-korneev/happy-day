from django.contrib import admin
from apps.openrouter.models import Token, AIModel, Message


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_secure']

    def token_secure(self, obj):
        return obj.token[:10] + '...'


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_id', 'token', 'is_default']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'model', 'model__token', 'created_at']

    def text_short(self, obj):
        return obj.text[:50] + '...'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
