# Generated by Django 5.0.6 on 2024-10-19 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0021_result_is_cheater'),
    ]

    operations = [
        migrations.AddField(
            model_name='dtmresult',
            name='is_cheater',
            field=models.BooleanField(default=False),
        ),
    ]
