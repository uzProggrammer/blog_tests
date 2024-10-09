# Generated by Django 5.0.6 on 2024-09-24 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizes', '0006_remove_dtm_results_dtmresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dtm',
            name='answers',
        ),
        migrations.AddField(
            model_name='answer',
            name='dtm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizes.dtm'),
        ),
    ]
