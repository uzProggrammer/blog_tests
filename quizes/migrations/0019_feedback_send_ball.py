# Generated by Django 5.0.6 on 2024-10-17 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0018_alter_answer_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='send_ball',
            field=models.BooleanField(default=False),
        ),
    ]
