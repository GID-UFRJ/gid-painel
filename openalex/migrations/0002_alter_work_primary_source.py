# Generated by Django 5.2.1 on 2025-06-01 02:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openalex', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='primary_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='openalex.primarysource'),
        ),
    ]
