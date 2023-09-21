import hashlib
from pathlib import Path

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

from document.models import Document


def calculate_hash(content: bytes):
    return hashlib.md5(content).hexdigest()


def save_faiss(filename):
    loader = UnstructuredHTMLLoader(filename)
    splitter = RecursiveCharacterTextSplitter()
    docs = loader.load_and_split(splitter)
    db = FAISS.from_documents(docs, OpenAIEmbeddings(chunk_size=16))
    folder_path: Path = settings.FAISS_ROOT / Path(filename).stem
    db.save_local(folder_path=folder_path.as_posix())
    return folder_path


class Command(BaseCommand):
    help = "Download files if source is a URL"

    def handle(self, *args, **options):
        documents = Document.objects.filter(file="", source__startswith="http")

        for document in documents:
            self.stdout.write(f"Processing {document.filename}...")
            response = requests.get(document.source)
            name = Path(document.source).stem
            filename = f"{name}.html" if name else "index.html"
            document.filename = filename

            if response.status_code == 200:
                temp_file = NamedTemporaryFile(delete=True)
                temp_file.write(response.content)
                temp_file.flush()

                document.hash = calculate_hash(response.content)
                document.file.save(filename, File(temp_file), save=True)
                document.file_size = temp_file.tell()
                faiss_store = save_faiss(settings.MEDIA_ROOT / document.file.name)
                document.faiss_store = faiss_store.name
                document.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully downloaded {document.filename}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to download {document.filename}")
                )
