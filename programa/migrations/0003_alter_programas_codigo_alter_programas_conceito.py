# Generated by Django 5.2.1 on 2025-05-13 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programa', '0002_alter_programas_conceito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programas',
            name='codigo',
            field=models.CharField(max_length=13),
        ),
        migrations.AlterField(
            model_name='programas',
            name='conceito',
            field=models.CharField(max_length=2),
        ),
    ]
