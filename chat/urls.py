from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ConversationViewSet,
    SystemPromptViewSet,
    echo_message,
    get_conversation_messages,
    openai_message,
)

router = DefaultRouter()
router.register(r"system-prompts", SystemPromptViewSet)
router.register(r"conversations", ConversationViewSet)


urlpatterns = [
    path("echo/", echo_message, name="echo_message"),
    path("openai/", openai_message, name="openai_message"),
    path(
        "conversations/<int:conversation_id>/messages/",
        get_conversation_messages,
        name="conversation_messages",
    ),
    path("", include(router.urls)),
]
