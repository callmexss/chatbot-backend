from pathlib import Path

from django.conf import settings
from langchain.document_loaders import (
    PyPDFium2Loader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer

LOADER_DIC = {
    ".html": UnstructuredHTMLLoader,
    ".pdf": PyPDFium2Loader,
    ".epub": UnstructuredEPubLoader,
}


def save_faiss(filename):
    try:
        path = Path(filename)
        loader = LOADER_DIC[path.suffix](path.as_posix())
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        docs = loader.load_and_split(splitter)
        print(f"total {len(docs)} chunks.")
        db = FAISS.from_documents(docs, OpenAIEmbeddings(chunk_size=16))
        folder_path: Path = settings.FAISS_ROOT / Path(filename).stem
        db.save_local(folder_path=folder_path.as_posix())
        return folder_path
    except Exception as err:
        print(f"{err} for file {filename}")


def ingest_document(document: Document):
    if document.file and not document.get_faiss_store():
        print(f"Processing {document.file}...")
        doc_path = Path(document.file.path)
        if not document.filename:
            document.filename = doc_path.name
        document.file_size = document.file.size
        if faiss_store := save_faiss(settings.MEDIA_ROOT / document.file.name):
            document.faiss_store = faiss_store.name
        document.save()

        print(f"Successfully embedded {document.filename}")
    else:
        print("File not found or embedding already exists for " + document.filename)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by("-created_at")
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        action = request.query_params.get("action")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        if action == "embed":
            document = Document.objects.get(id=serializer.data["id"])
            ingest_document(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDocumentsList(generics.ListAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Document.objects.filter(user=user).order_by("-created_at")
