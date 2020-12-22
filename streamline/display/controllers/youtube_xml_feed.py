from aiohttp import ClientSession, TCPConnector
import asyncio
import pypeln as pl
import xml.etree.ElementTree as ET
import time
from asgiref.sync import sync_to_async
from urllib.request import urlopen

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

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

async def fetchXML():

    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def fetch(url): # if only i knew how to use pub/sub, too bad
            async with session.get(url) as response:
                chunk = await response.read()
                tree = ET.ElementTree(ET.fromstring(chunk))
                root = tree.getroot()
                ns = '{http://www.w3.org/2005/Atom}'
                uncrawledVideoIds = []

                for entry in tree.iter(ns + 'entry'):
                    currVideoId = entry[1].text
                    try:
                        results = await sync_to_async(Video.objects.get, thread_sensitive=True)(pk=currVideoId)
                        # print('video found in db')
                    except ObjectDoesNotExist:
                        # fetch the video metadata with youtube api
                        # print('uncrawled video found: ' + currVideoId)
                        uncrawledVideoIds.append(currVideoId)
                return uncrawledVideoIds

        channels = await sync_to_async(Channel.objects.all)()
        urls = [
            'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channel.channelId
            for channel in channels
        ]

        stage = await pl.task.map(fetch, urls, workers=5) # 5 seems to be the safest
        data = list(stage)

        return data