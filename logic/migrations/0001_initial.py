# Generated by Django 4.2.11 on 2024-03-18 01:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('user_input', models.TextField()),
                ('response', models.TextField()),
            ],
        ),
    ]
