from django.urls import path, include
from .views import (
    echo_message,
    openai_message,
    get_conversation_messages,
    SystemPromptViewSet,
    ConversationViewSet,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'system-prompts', SystemPromptViewSet)
router.register(r'conversations', ConversationViewSet)


urlpatterns = [
    path('echo/', echo_message, name='echo_message'),
    path('openai/', openai_message, name='openai_message'),
    path(
        'conversations/<int:conversation_id>/messages/',
        get_conversation_messages,
        name='conversation_messages'
    ),
    path('', include(router.urls)),
]
