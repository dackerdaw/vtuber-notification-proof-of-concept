from django.db import models

class Channel(models.Model):
    channelId = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, null=True) # nullable, new channel might not have thumbnail in youtube api
    uploadPlaylist = models.CharField(max_length=100, null=True) # nullable, new channel might not have a video

    class Meta:
        app_label = 'display'
        
    def __str__(self):
        return f'{self.name}'