from django.contrib import admin

from .models import Conversation, Message, SystemPrompt

# Register your models here.


@admin.register(Conversation)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    ordering = ["-created_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["conversation", "content", "tokens", "message_type", "timestamp"]
    search_fields = ["content"]
    list_filter = ["message_type", "conversation"]
    ordering = ["-timestamp"]


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ["name", "content"]
    search_fields = ["name", "content"]
