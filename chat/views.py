from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import StreamingHttpResponse
from gptbase import basev2

from .models import Message
from .serializers import MessageSerializer


# Create your views here.
@api_view(['POST'])
def echo_message(request):
    content: str = request.data.get('content')
    message = Message(content=content, message_type='user')
    message.save()
    message = Message(content=content, message_type='bot')
    message.save()
    serializer = MessageSerializer(message)
    return Response(serializer.data)


assistant = basev2.Assistant()


def save_and_yield_original(gen):
    saved = []
    for item in gen:
        saved.append(item)
        yield item
    message_bot = Message(content=''.join(saved), message_type='bot')
    message_bot.save()


@api_view(['POST'])
def openai_message(request):
    content: str = request.data.get('content')
    message = Message(content=content, message_type='user')
    message.save()

    params = basev2.CompletionParameters(stream=True)
    chat_completion = assistant.ask(content, params=params)
    new_gen = save_and_yield_original(basev2.get_chunks(chat_completion))

    response = StreamingHttpResponse(
        (chunk for chunk in new_gen),
        content_type="text/plain"
    )

    return response

