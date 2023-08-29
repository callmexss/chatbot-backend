from django.http import StreamingHttpResponse
from gptbase import basev2
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Message
from .serializers import MessageSerializer


class ChatManager:
    def __init__(self):
        self.assistant = basev2.ChatAssistant()

    @staticmethod
    def save_message(content, message_type):
        message = Message(content=content, message_type=message_type)
        message.save()
        return message

    def save_and_yield_original(self, gen):
        saved = []
        for item in gen:
            saved.append(item)
            yield item
        message = ''.join(saved)
        self.save_message(message, 'bot')
        self.assistant.q.append(self.assistant.build_assistant_message(message))

    def echo_reply(self, content):
        message = self.save_message(content, 'user')
        message = self.save_message(content, 'bot')
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def openai_reply(self, content, system_prompt=''):
        self.assistant.q.append(self.assistant.build_user_message(content))
        self.save_message(content, 'user')

        completion_params = basev2.CompletionParameters(stream=True)
        chat_completion = self.assistant.ask(
            self.assistant.q,
            system_prompt=system_prompt,
            params=completion_params
        )
        
        new_gen = self.save_and_yield_original(basev2.get_chunks(chat_completion))

        return StreamingHttpResponse(
            (chunk for chunk in new_gen),
            content_type="text/plain"
        )


chat_manager = ChatManager()


@api_view(['POST'])
def echo_message(request):
    content: str = request.data.get('content')
    return chat_manager.echo_reply(content)


@api_view(['POST'])
def openai_message(request):
    content: str = request.data.get('content')
    system_prompt: str = request.data.get('system_prompt', '')
    return chat_manager.openai_reply(content, system_prompt=system_prompt)
