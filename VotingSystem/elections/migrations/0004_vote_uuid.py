# Generated by Django 5.0.4 on 2024-04-26 11:10

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0003_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]