# Generated by Django 4.1.5 on 2023-09-24 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0008_alter_document_faiss_store"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="file",
            field=models.FileField(blank=True, max_length=1024, upload_to="documents/"),
        ),
        migrations.AlterField(
            model_name="document",
            name="filename",
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]
