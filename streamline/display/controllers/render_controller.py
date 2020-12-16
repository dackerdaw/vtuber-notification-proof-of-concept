from django.http import HttpResponseRedirect
from django.shortcuts import render

from display.models.channel import Channel
from display.forms.find_channel import findChannel

def index(request):

    data = {
    }

    return render(request, 'base/base.html', context=data)

def channelsIndex(request):
    channels = Channel.objects.all()

    if request.method == 'POST':
        form = findChannel(request.POST)
        if form.is_valid():
            channelId = form.cleaned_data['channelId']
            try:
                selectedChannel = Channel.objects.get(pk=channelId)
                print("channel found in db")
            except:
                print("channel not found in db")
            return HttpResponseRedirect('/thanks/')
    else:
        form = findChannel()

    data = {
        'form':form,
        'channels':channels,
    }

    return render(request, 'channel/index.html', context=data)
