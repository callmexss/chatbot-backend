from django.contrib import admin

from .models import Document

# Register your models here.


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filename",
        "file",
        "source",
        "user",
        "faiss_store",
        "file_type",
        "file_size",
        "uploaded_at",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "filename",
        "source",
    )
