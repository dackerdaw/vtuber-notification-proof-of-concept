from aiohttp import ClientSession, TCPConnector
import asyncio
import sys
import pypeln as pl
import xml.etree.ElementTree as ET
import time
from asgiref.sync import sync_to_async

from display.models.channel import Channel
from display.models.video import Video

def get_url(filename):
    with open(filename) as file:
        urls = [line.rstrip('\n') for line in file]
        return urls

async def main():

    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def fetch(url):
            async with session.get(url) as response:
                chunk = await response.read()
                tree = ET.ElementTree(ET.fromstring(chunk))
                root = tree.getroot()
                ns = '{http://www.w3.org/2005/Atom}'
                uncrawledVideoIds = []

                for entry in tree.iter(ns + 'entry'):
                    currVideoId = entry[1].text
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

from django.http import HttpResponse
def utama(request):
    start_time = time.time()
    data = asyncio.run(main())
    print(len(data)) # should return 72 items
    print(len(data[0])) # should return 15 items, unless it's a really new channel
    end_time = time.time() - start_time
    return HttpResponse(end_time)
