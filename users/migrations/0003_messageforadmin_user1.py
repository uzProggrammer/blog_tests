# Generated by Django 5.0.6 on 2024-10-15 10:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_messageforadmin'),
    ]

    operations = [
        migrations.AddField(
            model_name='messageforadmin',
            name='user1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages_for_user1', to=settings.AUTH_USER_MODEL),
        ),
    ]
