from django.db import models

# Create your models here.
class Clients(models.Model):
    # Maybe should implement one-to-one relation which would symbolize connection(self.channel_name, anon.channel_name)
    channel_name = models.CharField(max_length=100)
    is_busy = models.BooleanField()
    anon_channel_name = models.CharField(max_length=100, default=None, null=True)

    def __str__(self):
        return self.channel_name