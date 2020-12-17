from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from display.models.channel import Channel
from display.models.video import Video

from .youtube_xml_feed import fetchChannelXML, fetchRecentFeedsXML
from .youtube_api_calls import fetchChannelAPI, fetchPlaylistItemsAPI, fetchVideosAPI

def confirmSaveChannel(request, channelId):
    if request.method == 'POST':
        fetchedChannel = fetchChannelAPI(channelId)
        newChannel = Channel(channelId=fetchedChannel[0], name=fetchedChannel[1], icon=fetchedChannel[2], uploadPlaylist=fetchedChannel[3])
        try:
            # save the channel and all the uploaded videos into db
            newChannel.save()
            fetchedVideos = fetchPlaylistItemsAPI(newChannel.uploadPlaylist)
            
            newVideos = []
            for item in fetchedVideos:
                currVideoId = item['snippet']['resourceId']['videoId']
                currTitle = item['snippet']['title']
                currThumbnail = item['snippet']['thumbnails']['medium']['url']
                currActualEndTime = item['snippet']['publishedAt'] # publishedAt of an upload playlist item is the time it was posted to the playlist

                # this also doesn't raise any error, it just ignores it?
                newVideo = Video(videoId=currVideoId, channelId=newChannel, title=currTitle, thumbnail=currThumbnail, actualEndTime=currActualEndTime)
                try:
                    newVideo.save()
                except:
                    print("Something went wrong idk")
                    return HttpResponseRedirect(reverse('channel-index'))

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

def updateRecentFeedsHelper(channelId):
    uncrawledVideoIds = fetchRecentFeedsXML(channelId)
    if uncrawledVideoIds:
        # call youtube api for videos with the following videoId (multiple video ids are ok too)
        videoIdString = ",".join(uncrawledVideoIds)
        items = fetchVideosAPI(videoIdString)

        selectedChannel = Channel.objects.get(pk=channelId)

        for item in items:
            currVideoId = item['id']
            currChannelId = selectedChannel
            currTitle = item['snippet']['title']
            currThumbnail = item['snippet']['thumbnails']['medium']['url']
            currPublishedAt = item['snippet']['publishedAt']
            currLiveBroadcastContent = item['snippet']['liveBroadcastContent']
            try:
                currScheduledStartTime = item['liveStreamingDetails']['scheduledStartTime']
            except:
                currScheduledStartTime = None

            try:
                currActualStartTime = item['liveStreamingDetails']['actualStartTime']
            except:
                currActualStartTime = None

            try:
                currActualEndTime = item['liveStreamingDetails']['actualEndTime']
            except:
                currActualEndTime = None

            newVideo = Video(
                videoId=currVideoId,
                channelId=currChannelId,
                title=currTitle,
                thumbnail=currThumbnail,
                publishedAt=currPublishedAt,
                liveBroadcastContent=currLiveBroadcastContent,
                scheduledStartTime=currScheduledStartTime,
                actualStartTime=currActualStartTime,
                actualEndTime=currActualEndTime,
            )

            try:
                newVideo.save()
            except:
                print("Something went wrong idk")
                return HttpResponseRedirect(reverse('channel-index'))
            
        return len(items)

    else:
        return 0

def updateRecentFeedsChannel(request, channelId):
    newlyCrawledVideos = updateRecentFeedsHelper(channelId)
    if newlyCrawledVideos > 0:
        messages.info(request, '%d new video(s) found.' % newlyCrawledVideos)
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))

def updateRecentFeedsAll(request):
    channels = Channel.objects.all()
    newlyCrawledVideos = 0

    for channel in channels:
        newlyCrawledVideos += updateRecentFeedsHelper(channel.channelId)

    if newlyCrawledVideos > 0:
        messages.info(request, '%d new video(s) found.' % newlyCrawledVideos)
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    return HttpResponseRedirect(reverse('index'))
