from django.db import models
from display.models.channel import Channel

class Video(models.Model):
    BROADCAST_STATUS = [
        ('live', 'Live'),
        ('none', 'Archived'),
        ('upcoming', 'Upcoming'),
    ]

    videoId = models.CharField(max_length=100, primary_key=True)
    channelId = models.ForeignKey(Channel, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    thumbnail = models.CharField(max_length=100)
    publishedAt = models.DateTimeField(null=True) # ISO 8601 format
    liveBroadcastContent = models.CharField(max_length=10, choices=BROADCAST_STATUS, default='none')
    scheduledStartTime = models.DateTimeField(null=True) # ISO 8601 format
    actualStartTime = models.DateTimeField(null=True) # ISO 8601 format
    actualEndTime = models.DateTimeField(null=True) # ISO 8601 format

    class Meta:
        app_label = 'display'
        
    def __str__(self):
        return f'{self.title}'