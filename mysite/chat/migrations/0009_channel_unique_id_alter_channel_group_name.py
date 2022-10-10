# Generated by Django 4.0.5 on 2022-10-10 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_alter_channel_group_name_alter_group_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='unique_id',
            field=models.IntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='channel',
            name='group_name',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='channels', to='chat.group'),
        ),
    ]