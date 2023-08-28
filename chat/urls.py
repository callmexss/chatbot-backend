from django.urls import path
from .views import echo_message, openai_message

urlpatterns = [
    path('echo/', echo_message, name='echo_message'),
    path('openai/', openai_message, name='openai_message'),
]
