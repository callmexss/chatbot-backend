from django.contrib import admin
from .models import Message, SystemPrompt

# Register your models here.

admin.site.register(Message)
admin.site.register(SystemPrompt)
