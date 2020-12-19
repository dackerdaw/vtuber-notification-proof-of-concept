from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from display.models.channel import Channel
from display.models.video import Video

from .youtube_xml_feed import fetchChannelXML, fetchRecentFeedsXML
from .youtube_api_calls import fetchChannelAPI, fetchPlaylistItemsAPI, fetchVideosAPI
import display.controllers.debug_helper

@display.controllers.debug_helper.st_time
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
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect(reverse('channel-index'))

            # don't forget to implement the message in the template
            messages.info(request, 'Channel saved. %d archived video(s) found. %d YouTube API quota spent' % (len(fetchedVideos), display.controllers.debug_helper.API_CALLS_MADE))
            display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
            return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))

        except Exception as e:
            print(e)
            # implement the error msg!!!! but i dont even know what kind of error this'll produce, if any.
            return HttpResponseRedirect(reverse('channel-index'))

    else:
        try:
            fetchedChannel = fetchChannelXML(channelId)
            # print("channel found in youtube")
        except Exception as e:
            print(e)
            messages.info(request, 'Channel associated with the ID not found on our database nor on YouTube!')
            display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
            # don't forget to implement the message in the template
            return HttpResponseRedirect(reverse('channel-index'))

    data = {
        'fetchedChannel':fetchedChannel,
    }

    return render(request, 'confirm/confirm_save_channel.html', context=data)

def updateRecentFeedsHelper(channelId):
    uncrawledVideoIds = fetchRecentFeedsXML(channelId)
    if uncrawledVideoIds:
        # call youtube api for videos with the following videoId (multiple video ids are ok too up to 50 ids)
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
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('channel-index'))
            
        return len(items)

    else:
        return 0

@display.controllers.debug_helper.st_time
def updateRecentFeedsChannel(request, channelId):
    newlyCrawledVideos = updateRecentFeedsHelper(channelId)
    if newlyCrawledVideos > 0:
        messages.info(request, 'Channel crawled. %d new video(s) found. %d YouTube API quota spent' % (newlyCrawledVideos, display.controllers.debug_helper.API_CALLS_MADE))
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))

# Yield successive n-sized 
# chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

@display.controllers.debug_helper.st_time
def updateRecentFeedsAll(request):
    channels = Channel.objects.all()
    newlyCrawledVideoIdList = []

    for channel in channels:
        newlyCrawledVideoIdList.extend(fetchRecentFeedsXML(channel.channelId))
    
    # YouTube API videos.list() allows up to 50 videoIds per call.
    # since we crawl all channels periodically, it shouldn't exceeds 50.
    # but for testing purposes, we might crawl all channels that has never been 
    # crawled which potentially yields more than 50 uncrawled videos
    numOfVids = len(newlyCrawledVideoIdList)

    if numOfVids > 0:
        dividedChunks = list(divide_chunks(newlyCrawledVideoIdList, 50))
        for chunk in dividedChunks:
            videoIdString = ",".join(chunk)
            items = fetchVideosAPI(videoIdString)

            for item in items:
                currVideoId = item['id']
                currChannelId = item['snippet']['channelId']
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
                    # channelId=currChannelId,
                    title=currTitle,
                    thumbnail=currThumbnail,
                    publishedAt=currPublishedAt,
                    liveBroadcastContent=currLiveBroadcastContent,
                    scheduledStartTime=currScheduledStartTime,
                    actualStartTime=currActualStartTime,
                    actualEndTime=currActualEndTime,
                )
                newVideo.channelId_id = currChannelId

                try:
                    newVideo.save()
                except Exception as e:
                    print(e)
                    return HttpResponseRedirect(reverse('channel-index'))
                
        messages.info(request, 'All %d channel(s) crawled. %d new video(s) found. %d YouTube API quota spent' % (len(channels), numOfVids, display.controllers.debug_helper.API_CALLS_MADE))
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('index'))
