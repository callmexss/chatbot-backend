import hashlib
import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("img", "Image"),
        ("doc", "Document"),
        ("html", "HTML"),
        # ... more types
    ]

    filename = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to="documents/", blank=True)
    hash = models.CharField(max_length=64, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=8192, blank=True)
    faiss_store = models.CharField(max_length=8192, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        if self.file:
            hasher = hashlib.sha256()
            for chunk in self.file.chunks():
                hasher.update(chunk)
            self.file_hash = hasher.hexdigest()

        super(Document, self).save(*args, **kwargs)

    def get_faiss_store(self):
        if self.faiss_store:
            return settings.FAISS_ROOT / self.faiss_store


@receiver(pre_delete, sender=Document)
def delete_file(sender, instance, **kwargs):
    if instance.file:
        if Path(instance.file.path).exists():
            os.remove(instance.file.path)
