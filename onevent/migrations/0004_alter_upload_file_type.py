# Generated by Django 4.2.16 on 2024-12-03 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onevent', '0003_upload_file_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='file_type',
            field=models.CharField(blank=True, default='unknown', max_length=50),
        ),
    ]
