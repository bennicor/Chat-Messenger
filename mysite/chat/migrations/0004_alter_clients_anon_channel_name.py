# Generated by Django 4.0.5 on 2022-07-26 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_clients_anon_channel_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clients',
            name='anon_channel_name',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
