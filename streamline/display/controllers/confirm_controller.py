from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from display.models.channel import Channel

from .youtube_xml_feed import fetchChannelXML
from .youtube_api_calls import fetchChannelAPI

def confirmSaveChannel(request, channelId):
    if request.method == 'POST':
        fetchedChannel = fetchChannelAPI(channelId)
        newChannel = Channel(channelId=fetchedChannel[0], name=fetchedChannel[1], icon=fetchedChannel[2], uploadPlaylist=fetchedChannel[3])
        try:
            newChannel.save()
            return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))
        except:
            print("An exception occurred")
            # implement the error msg!!!! but i dont even know what kind of error this'll produce, if any.
            return HttpResponseRedirect(reverse('channel-index'))

    else:
        try:
            fetchedChannel = fetchChannelXML(channelId)
            print("channel found in youtube")
        except:
            print("Invalid youtube channel id or something (idk the exact exception)")
            messages.info(request, 'Channel associated with the ID not found on our database nor on YouTube!')
            # don't forget to implement the message in the template
            return HttpResponseRedirect(reverse('channel-index'))

    data = {
        'fetchedChannel':fetchedChannel,
    }

    return render(request, 'confirm/confirm_save_channel.html', context=data)