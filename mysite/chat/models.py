from django.db import models

# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Channel(models.Model):
    channel_name = models.CharField(max_length=100)
    is_busy = models.BooleanField()
    group_name = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, default=None, related_name="channels")
    user_id = models.IntegerField()

    def __str__(self):
        return self.channel_name

class MessageLine(models.Model):
    message = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    time_created = models.TimeField()

    def __str__(self):
        return self.message

