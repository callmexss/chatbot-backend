from django.contrib import admin
from .models import Message, SystemPrompt, Session

# Register your models here.

admin.site.register(Message)
admin.site.register(SystemPrompt)
admin.site.register(Session)
