import hashlib
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from langchain.document_loaders import (
    PyPDFium2Loader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    TextLoader,
)
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

from document.models import Document

LOADER_DIC = {
    ".html": UnstructuredHTMLLoader,
    ".pdf": PyPDFium2Loader,
    ".epub": UnstructuredEPubLoader,
    ".txt": TextLoader,
}


def calculate_hash(content: bytes):
    return hashlib.md5(content).hexdigest()


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


class Command(BaseCommand):
    help = "Embed document if file is not None."

    def handle(self, *args, **options):
        documents = Document.objects.all()

        for document in documents:
            try:
                if document.file and not document.get_faiss_store():
                    self.stdout.write(f"Processing {document.file}...")
                    doc_path = Path(document.file.path)
                    if not document.filename:
                        document.filename = doc_path.name
                    document.file_size = document.file.size
                    if faiss_store := save_faiss(settings.MEDIA_ROOT / document.file.name):
                        document.faiss_store = faiss_store.name
                    document.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully embedded {document.filename}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "File not found or embedding already exists for "
                            + document.filename
                        )
                    )
            except Exception as err:
                print(err)
