from rest_framework import serializers

from .models import Conversation, Message, SystemPrompt


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation", "content", "message_type", "timestamp"]


class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = ["id", "name", "content"]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "user", "name", "created_at"]
