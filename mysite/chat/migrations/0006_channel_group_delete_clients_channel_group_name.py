# Generated by Django 4.0.5 on 2022-10-09 04:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_remove_clients_anon_channel_name_clients_group_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=100)),
                ('is_busy', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(default=None, max_length=20, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Clients',
        ),
        migrations.AddField(
            model_name='channel',
            name='group_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.group'),
        ),
    ]
