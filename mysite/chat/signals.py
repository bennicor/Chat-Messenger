from django.dispatch import receiver
from django.db.models.signals import post_delete
from chat.models import Channel, Group


@receiver(post_delete, sender=Channel)
def delete_connected_channels(sender, instance, **kwargs):
    # Delete group if all related channels are deleted
    if instance.group_name:
        group = Group.objects.get(pk=instance.group_name.pk)
        
        related_channels = group.channels.all()
        if not related_channels:
            group.delete()
