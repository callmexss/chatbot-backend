from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import StreamingHttpResponse
from gptbase import basev2

from .models import Message

assistant = basev2.Assistant()
assistant = basev2.ChatAssistant()


def save_message(content, message_type):
    message = Message(content=content, message_type=message_type)
    message.save()
    return message


def save_and_yield_original(gen):
    saved = []
    for item in gen:
        saved.append(item)
        yield item
    message = ''.join(saved)
    save_message(message, 'bot')
    assistant.q.append(assistant.build_assistant_message(message))


def handle_post_request(request, reply_function):
    content: str = request.data.get('content')
    save_message(content, 'user')
    return reply_function(content)


def echo_reply(content):
    save_message(content, 'bot')
    return Response({"content": content, "message_type": "bot"})


def openai_reply(content):
    assistant.q.append(assistant.build_user_message(content))

    params = basev2.CompletionParameters(stream=True)
    chat_completion = assistant.ask(assistant.q, params=params)
    new_gen = save_and_yield_original(basev2.get_chunks(chat_completion))

    return StreamingHttpResponse(
        (chunk for chunk in new_gen),
        content_type="text/plain"
    )


@api_view(['POST'])
def echo_message(request):
    return handle_post_request(request, echo_reply)


@api_view(['POST'])
def openai_message(request):
    return handle_post_request(request, openai_reply)
