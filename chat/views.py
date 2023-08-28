from rest_framework.response import Response
from rest_framework.decorators import api_view
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


@api_view(['POST'])
def openai_message(request):
    content: str = request.data.get('content')
    message = Message(content=content, message_type='user')
    message.save()
    chat_completion = assistant.ask(content)
    reply = basev2.get_message(chat_completion)
    message = Message(content=reply, message_type='bot')
    message.save()
    serializer = MessageSerializer(message)
    return Response(serializer.data)

