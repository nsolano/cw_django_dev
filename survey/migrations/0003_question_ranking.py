# Generated by Django 3.2.5 on 2023-11-28 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_questionfeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='ranking',
            field=models.PositiveIntegerField(default=0, verbose_name='Ranking'),
        ),
    ]
