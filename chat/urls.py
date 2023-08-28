from django.urls import path
from .views import echo_message

urlpatterns = [
    path('echo/', echo_message, name='echo_message'),
]
