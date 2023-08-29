from django.urls import path, include
from .views import (
    echo_message,
    openai_message,
    SystemPromptViewSet
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'system-prompts', SystemPromptViewSet)


urlpatterns = [
    path('echo/', echo_message, name='echo_message'),
    path('openai/', openai_message, name='openai_message'),
    path('', include(router.urls)),
]
