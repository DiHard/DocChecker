# Generated by Django 5.1 on 2024-08-21 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_zacup'),
    ]

    operations = [
        migrations.RenameField(
            model_name='zacup',
            old_name='tg_id',
            new_name='doc_number',
        ),
    ]
