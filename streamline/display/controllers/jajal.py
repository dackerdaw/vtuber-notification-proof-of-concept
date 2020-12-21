import aiohttp
import asyncio
import async_timeout
import os
import xml.etree.ElementTree as ET

from display.models.channel import Channel

async def download_coroutine(session, url):
    async with session.get(url) as response:
        chunk = await response.text()
        tree = ET.ElementTree(ET.fromstring(chunk))
        root = tree.getroot()
        currChannelName = root[3].text
        print(currChannelName)

channels = (
    'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channel.channelId for channel in Channel.objects.all()
)


async def main():
    urls = channels
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(download_coroutine(session, url))
            # await download_coroutine(session, url)
            tasks.append(task)
        await asyncio.wait(tasks)

from django.http import HttpResponse
import time
def utama(request):
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time() - start_time
    return HttpResponse(end_time)