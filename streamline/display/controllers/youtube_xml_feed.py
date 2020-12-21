from urllib.request import urlopen
import itertools
import xml.etree.ElementTree as ET

from django.shortcuts import render
from asgiref.sync import sync_to_async

from display.models.channel import Channel
from display.models.video import Video

def fetchChannelXML(channelId):

    url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channelId
    var_url = urlopen(url)
    tree = ET.parse(var_url)
    root = tree.getroot()

    currChannelId = root[2].text
    currChannelName = root[3].text

    return (currChannelId, currChannelName)

def fetchRecentFeedsXML(channelId):

    url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channelId
    var_url = urlopen(url)
    tree = ET.parse(var_url)
    ns = '{http://www.w3.org/2005/Atom}'
    uncrawledVideoIds = []

    # there must be a better way for this, but too bad i guess
    for entry in tree.iter(ns + 'entry'):
        currVideoId = entry[1].text
        try:
            vidya = Video.objects.get(pk=currVideoId)
            # print('video found in db')
        except:
            # fetch the video metadata with youtube api
            # print('uncrawled video found: ' + currVideoId)
            uncrawledVideoIds.append(currVideoId)

    return uncrawledVideoIds

@sync_to_async
def fetchRecentFeedsXMLAsync(channelId):

    url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channelId
    var_url = urlopen(url)
    tree = ET.parse(var_url)
    ns = '{http://www.w3.org/2005/Atom}'
    uncrawledVideoIds = []

    # there must be a better way for this, but too bad i guess
    for entry in tree.iter(ns + 'entry'):
        currVideoId = entry[1].text
        try:
            vidya = Video.objects.get(pk=currVideoId)
            # print('video found in db')
        except:
            # fetch the video metadata with youtube api
            # print('uncrawled video found: ' + currVideoId)
            uncrawledVideoIds.append(currVideoId)

    return uncrawledVideoIds