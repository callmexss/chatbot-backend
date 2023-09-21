import os

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand

from document.models import Document


class Command(BaseCommand):
    help = "Download files if source is a URL"

    def handle(self, *args, **options):
        documents = Document.objects.filter(file="", source__startswith="http")

        for document in documents:
            self.stdout.write(f"Processing {document.filename}...")
            response = requests.get(document.source)

            if response.status_code == 200:
                # Create a temporary file
                temp_file = NamedTemporaryFile(delete=True)
                temp_file.write(response.content)
                temp_file.flush()

                # Save the file to the model
                file_name = os.path.basename(document.source)
                document.file.save(file_name, File(temp_file), save=True)
                document.file_size = temp_file.tell()
                document.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully downloaded {document.filename}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to download {document.filename}")
                )
