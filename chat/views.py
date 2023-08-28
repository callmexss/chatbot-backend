from rest_framework.response import Response
from rest_framework.decorators import api_view

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
