from rest_framework import serializers
from .models import Message, SystemPrompt

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'timestamp']


class SystemPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemPrompt
        fields = ['id', 'name', 'content']
