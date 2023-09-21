from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ("pdf", "PDF"),
        ("img", "Image"),
        ("doc", "Document"),
        # ... more types
    ]

    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=8192, blank=True)
    faiss_store = models.FilePathField(path=settings.FAISS_ROOT, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename
