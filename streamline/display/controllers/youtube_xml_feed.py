from aiohttp import ClientSession, TCPConnector
import asyncio
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from asgiref.sync import sync_to_async

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

async def fetch(url, session): # if only i knew how to use pub/sub, too bad
    async with session.get(url) as response:
        chunk = await response.read()
        tree = ET.ElementTree(ET.fromstring(chunk))
        root = tree.getroot()
        ns = '{http://www.w3.org/2005/Atom}'
        uncrawledVideoIds = []

        for entry in tree.iter(ns + 'entry'):
            currVideoId = entry[1].text
            # Check if the video already exists in our database
            try:
                results = await sync_to_async(Video.objects.get, thread_sensitive=True)(pk=currVideoId)
            except ObjectDoesNotExist:
                # collect all the uncrawled videos
                uncrawledVideoIds.append(currVideoId)
        return uncrawledVideoIds


async def fetchXMLAsync():

    channels = await sync_to_async(Channel.objects.all)()
    urls = [
        'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channel.channelId
        for channel in channels
    ]
    tasks = []
    async with ClientSession(connector=TCPConnector(limit=5)) as session: # 5 seems to be the safest for my 3rd world country-tier internet

        for url in urls:
            task = asyncio.create_task(fetch(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses

def fetchXML():
    return asyncio.run(fetchXMLAsync())