# Generated by Django 5.1 on 2024-08-23 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0007_zacup_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='tg_nic',
            field=models.CharField(default=1, max_length=250, verbose_name='Ник в телеграм'),
            preserve_default=False,
        ),
    ]
