from typing import Optional

from django.http import StreamingHttpResponse
from gptbase import basev2
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import MergerRetriever
from langchain.vectorstores.faiss import FAISS
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation, Document, Message, SystemPrompt
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    SystemPromptSerializer,
)

CONTEXT_CHAT_PROMPT = """Given the context below:

{context}

Answer user's question: {question}.

If you don't know the answer, just say you don't know.
Dont make up.
"""


class ChatManager:
    def __init__(self, memory_turns=8):
        self.assistant = basev2.ChatAssistant(memory_turns=memory_turns)

    def initialize_conversation(self, conversation_id, user):
        conversation, _ = Conversation.objects.get_or_create(
            id=conversation_id, user=user
        )
        messages = conversation.messages.all().order_by("timestamp")
        max_len = self.assistant.q.maxlen
        self.assistant.q.clear()
        print("initialize chat assistant")
        start_idx = max(0, len(messages) - max_len)
        for message in messages[start_idx:]:
            role = "user" if message.message_type == "user" else "assistant"
            self.assistant.q.append(
                self.assistant.build_message(role=role, message=message.content)
            )
        print(self.assistant.q)

    @staticmethod
    def save_message(
        content,
        message_type,
        conversation,
        tokens=0,
        system_prompt="",
        context="",
        documents=None,
    ):
        message = Message(
            content=content,
            message_type=message_type,
            conversation=conversation,
            tokens=tokens,
            system_prompt=system_prompt,
            context=context,
        )
        message.save()
        if documents:
            message.documents.set(documents)
        return message

    def save_and_yield_original(self, gen, conversation, model):
        saved = []
        yield f"{conversation.id}|||".encode()
        for item in gen:
            saved.append(item)
            yield item
        message = "".join(saved)
        tokens = basev2.count_tokens(message, model)
        self.save_message(message, "bot", conversation, tokens)
        self.assistant.q.append(self.assistant.build_assistant_message(message))

    def create_and_name_conversation(self, first_sentence, user):
        system_prompt = (
            "ChatGPT, generate a short name for a new "
            "conversation based on the following sentence. "
            "The name should not be more than 10 words."
        )
        completion_params = basev2.CompletionParameters()
        response = self.assistant.ask(
            [self.assistant.build_user_message(first_sentence)],
            system_prompt=system_prompt,
            params=completion_params,
        )
        generated_name = basev2.get_message(response)

        new_conversation = Conversation.objects.create(name=generated_name, user=user)
        self.initialize_conversation(new_conversation.id, user)
        return new_conversation

    def echo_reply(self, content):
        conversation, _ = Conversation.objects.get_or_create(name="test chat")
        message = self.save_message(content, "user", conversation)
        message = self.save_message(content, "bot", conversation)
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def openai_reply(
        self, content, conversation, model="gpt-3.5-turbo-0613", system_prompt=""
    ):
        self.assistant.q.append(self.assistant.build_user_message(content))
        tokens = basev2.num_tokens_from_messages(self.assistant.q, model)
        self.save_message(content, "user", conversation, tokens)

        completion_params = basev2.CompletionParameters(stream=True, model=model)
        if tokens > 2500:
            completion_params.model = "gpt-3.5-turbo-16k-0613"
        chat_completion = self.assistant.ask(
            self.assistant.q, system_prompt=system_prompt, params=completion_params
        )

        new_gen = self.save_and_yield_original(
            basev2.get_chunks(chat_completion), conversation, model
        )

        return StreamingHttpResponse(new_gen, content_type="text/plain")

    def openai_doc_reply(
        self,
        content,
        conversation,
        model="gpt-3.5-turbo-0613",
        documents: Optional[list[Document]] = None,
        system_prompt="",
    ):
        li = []
        for document in documents:
            db_path = document.get_faiss_store()
            db: FAISS = FAISS.load_local(db_path, OpenAIEmbeddings(chunk_size=16))
            li.append(db.as_retriever())
        lotr = MergerRetriever(li)
        document_li = lotr.get_relevant_documents(content)
        context_li = []
        for i, doc in enumerate(document_li):
            context_li.append(f"\n context {i}: \n{doc.page_content}\n---\n")
        context = "\n".join(context_li)
        new_content = CONTEXT_CHAT_PROMPT.format(question=content, context=context)
        self.assistant.q.append(self.assistant.build_user_message(new_content))
        tokens = basev2.num_tokens_from_messages(self.assistant.q, model)
        self.save_message(
            content,
            "user",
            conversation,
            tokens,
            system_prompt=system_prompt,
            context=new_content,
            documents=documents,
        )

        completion_params = basev2.CompletionParameters(stream=True, model=model)
        if tokens > 2500:
            completion_params.model = "gpt-3.5-turbo-16k-0613"
        chat_completion = self.assistant.ask(
            self.assistant.q, system_prompt=system_prompt, params=completion_params
        )
        self.assistant.q.pop()
        self.assistant.q.append(self.assistant.build_user_message(new_content))

        new_gen = self.save_and_yield_original(
            basev2.get_chunks(chat_completion), conversation, model
        )

        return StreamingHttpResponse(new_gen, content_type="text/plain")


DEFAULT_CONVERSATION_ID = 1
chat_manager = ChatManager()
conversation_name_manager = ChatManager()


@api_view(["POST"])
def echo_message(request):
    content: str = request.data.get("content")
    return chat_manager.echo_reply(content)


@api_view(["POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def openai_message(request):
    user = request.user
    content: str = request.data.get("content")
    model: str = request.data.get("model", "gpt-3.5-turbo-0613")
    system_prompt: str = request.data.get("system_prompt", "")
    conversation_id = request.data.get("conversation_id")
    document_ids = request.data.get("document_ids", None)

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        conversation = conversation_name_manager.create_and_name_conversation(
            content, user
        )

    if document_ids:
        documents = Document.objects.filter(id__in=document_ids)
        return chat_manager.openai_doc_reply(
            content,
            conversation,
            model,
            documents,
            system_prompt=system_prompt,
        )
    else:
        return chat_manager.openai_reply(
            content,
            conversation,
            model,
            system_prompt=system_prompt,
        )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_conversation_messages(request, conversation_id):
    user = request.user
    chat_manager.initialize_conversation(conversation_id, user)
    messages = Message.objects.filter(conversation_id=conversation_id).order_by(
        "timestamp"
    )
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


class SystemPromptViewSet(viewsets.ModelViewSet):
    queryset = SystemPrompt.objects.all().order_by("name")
    serializer_class = SystemPromptSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by("-created_at")
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        mutable_data = request.data.copy()
        mutable_data["user"] = user.id

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        new_conversation = Conversation.objects.get(id=serializer.data["id"])
        chat_manager.initialize_conversation(new_conversation.id, user)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()
