from tokenize import group
from django.dispatch import receiver
from django.db.models.signals import post_delete
from chat.models import Channel, Group

@receiver(post_delete, sender=Channel)
def test(sender, instance, **kwargs):
    if instance.group_name:
        group = Group.objects.get(pk=instance.group_name.pk)
        
        related_channels = group.channels.all()
        if not related_channels:
            group.delete()