# Generated by Django 4.1.5 on 2023-09-21 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0006_alter_document_file_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="filename",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
