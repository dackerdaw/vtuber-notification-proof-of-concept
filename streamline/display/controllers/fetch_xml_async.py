from aiohttp import ClientSession, TCPConnector
import asyncio
import pypeln as pl
import xml.etree.ElementTree as ET
import time
from asgiref.sync import sync_to_async

from display.models.channel import Channel
from display.models.video import Video

from django.core.exceptions import ObjectDoesNotExist

async def main():

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

'''
fetch the xml file from each channel's YouTube RSS feeds asynchronously.
return a list of videoId of new videos (doesn't make an API call)
'''
def utama():
    start_time = time.time()

    results = asyncio.run(main())
    videoIdList = []
    for channel in results:
        videoIdList.extend(channel)

    end_time = time.time() - start_time
    return videoIdList
