# Generated by Django 5.0.6 on 2024-09-21 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminlog',
            name='href',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
