from urllib.request import urlopen
import xml.etree.ElementTree as ET

from django.shortcuts import render

from display.models.channel import Channel

def fetchChannelXML(channelId):

    url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channelId
    var_url = urlopen(url)
    tree = ET.parse(var_url)
    root = tree.getroot()

    currChannelId = root[2].text
    currChannelName = root[3].text

    return (currChannelId, currChannelName)