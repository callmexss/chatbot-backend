# Generated by Django 4.1.5 on 2023-08-29 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_systemprompt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemprompt',
            name='content',
            field=models.TextField(max_length=4000),
        ),
        migrations.AlterField(
            model_name='systemprompt',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]