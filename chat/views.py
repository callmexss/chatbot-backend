from django.http import StreamingHttpResponse
from gptbase import basev2
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Message, SystemPrompt, Conversation
from .serializers import (
    MessageSerializer,
    SystemPromptSerializer,
    ConversationSerializer,
)


class ChatManager:
    def __init__(self):
        self.assistant = basev2.ChatAssistant()

    @staticmethod
    def save_message(content, message_type, conversation):
        message = Message(
            content=content, message_type=message_type, conversation=conversation
        )
        message.save()
        return message

    def save_and_yield_original(self, gen, conversation):
        saved = []
        for item in gen:
            saved.append(item)
            yield item
        message = ''.join(saved)
        self.save_message(message, 'bot', conversation)
        self.assistant.q.append(self.assistant.build_assistant_message(message))

    def echo_reply(self, content):
        conversation, _ = Conversation.objects.get_or_create(name="test chat")
        message = self.save_message(content, 'user', conversation)
        message = self.save_message(content, 'bot', conversation)
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def openai_reply(self, content, conversation, system_prompt=''):
        self.assistant.q.append(self.assistant.build_user_message(content))
        self.save_message(content, 'user', conversation)

        completion_params = basev2.CompletionParameters(stream=True)
        chat_completion = self.assistant.ask(
            self.assistant.q,
            system_prompt=system_prompt,
            params=completion_params
        )
        
        new_gen = self.save_and_yield_original(
            basev2.get_chunks(chat_completion), conversation
        )

        return StreamingHttpResponse(
            (chunk for chunk in new_gen),
            content_type="text/plain"
        )


DEFAULT_CONVERSATION_ID = 1
chat_manager = ChatManager()


@api_view(['POST'])
def echo_message(request):
    content: str = request.data.get('content')
    return chat_manager.echo_reply(content)


@api_view(['POST'])
def openai_message(request):
    content: str = request.data.get('content')
    system_prompt: str = request.data.get('system_prompt', '')
    conversation_id = request.data.get('conversation_id', DEFAULT_CONVERSATION_ID)
    conversation, _ = Conversation.objects.get_or_create(id=conversation_id)
    return chat_manager.openai_reply(content, conversation, system_prompt=system_prompt)


@api_view(['GET'])
def get_conversation_messages(request, conversation_id):
    messages = Message.objects.filter(
        conversation_id=conversation_id
    ).order_by('timestamp')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


class SystemPromptViewSet(viewsets.ModelViewSet):
    queryset = SystemPrompt.objects.all().order_by('name')
    serializer_class = SystemPromptSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer