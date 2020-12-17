from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from display.models.channel import Channel
from display.forms.find_channel_form import findChannelForm

from .youtube_xml_feed import fetchChannelXML

def index(request):

    data = {
    }

    return render(request, 'base/base.html', context=data)

def channelsIndex(request):

    if request.method == 'POST':
        form = findChannelForm(request.POST)
        if form.is_valid():
            channelId = form.cleaned_data['channelId']
            # check if channel exists in db, otherwise fetch with youtube xml feed
            try:
                selectedChannel = Channel.objects.get(pk=channelId)
                print("channel found in db")
                # display in another page
                return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))
            except:
                print("channel not found in db")
                # check if its a valid youtube channel, and asks if user want to save it and crawl it
                return HttpResponseRedirect(reverse('confirm-save-channel', args=[channelId]))

    else:
        form = findChannelForm()
    
    channels = Channel.objects.all()

    data = {
        'form':form,
        'channels':channels,
    }

    return render(request, 'channel/index.html', context=data)

def channelDetail(request, channelId):
    selectedChannel = Channel.objects.get(pk=channelId)

    data = {
        'selectedChannel':selectedChannel,
    }

    return render(request, 'channel/detail.html', context=data)
