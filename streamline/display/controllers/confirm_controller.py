from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q
from asgiref.sync import sync_to_async

import requests, asyncio, time

from display.models.channel import Channel
from display.models.video import Video

from .youtube_xml_feed import fetchChannelXML, fetchRecentFeedsXML, fetchXML
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
            # playlistItems.list() doesn't give full info of a video, you need videos.list() for that
            newlyCrawledVideoIdList = []
            fetchedVideos = fetchPlaylistItemsAPI(newChannel.uploadPlaylist)
            numOfVids = len(fetchedVideos)

            if numOfVids > 0:
                for item in fetchedVideos:
                    newlyCrawledVideoIdList.append(item['snippet']['resourceId']['videoId'])

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
                            channelId=newChannel,
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


            # don't forget to implement the message in the template
            messages.info(request, 'Channel saved. %d archived video(s) found. %d YouTube API quota spent' % (len(fetchedVideos), display.controllers.debug_helper.API_CALLS_MADE))
            display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
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
            display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
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

# look for new videos of a channel from the XML feed
@display.controllers.debug_helper.st_time
def updateRecentFeedsChannel(request, channelId):
    newlyCrawledVideos = updateRecentFeedsHelper(channelId)
    if newlyCrawledVideos > 0:
        messages.info(request, 'Channel crawled. %d new video(s) found. %d YouTube API quota spent' % (newlyCrawledVideos, display.controllers.debug_helper.API_CALLS_MADE))
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))

# Update the metadata of upcoming and live video of a channel, use this to figure 
# out if an upcoming live stream has started or otherwise, ongoing live stream has ended
@display.controllers.debug_helper.st_time
def updateWatchlistChannel(request, channelId):
    selectedChannel = Channel.objects.get(pk=channelId)
    watchlist = Video.objects.filter(Q(channelId=selectedChannel) , Q(liveBroadcastContent='live') | Q(liveBroadcastContent='upcoming'))
    # assuming that the watchlist contains no longer than 50 items
    watchlistedVideoIdList = [video.videoId for video in watchlist]
    videoIdString = ",".join(watchlistedVideoIdList)

    # what would happen if the video is unarchived?
    items = fetchVideosAPI(videoIdString)

    for item in items:
        currVideoId = item['id']
        # currChannelId = item['snippet']['channelId'] # see what happens if you don't specify the channel object
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

        currVideo = Video.objects.get(pk=currVideoId)
        currVideo.title = currTitle
        currVideo.thumbnail = currThumbnail
        currVideo.publishedAt = currPublishedAt
        currVideo.liveBroadcastContent = currLiveBroadcastContent
        currVideo.scheduledStartTime = currScheduledStartTime
        currVideo.actualStartTime = currActualStartTime
        currVideo.actualEndTime = currActualEndTime

        try:
            currVideo.save()
        except Exception as e:
            print(e)
            return HttpResponseRedirect(reverse('channel-index'))


    if len(items) > 0:
        messages.info(request, 'Watchlish updated. %d video(s) updated. %d YouTube API quota spent' % (len(items), display.controllers.debug_helper.API_CALLS_MADE))
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('channel-detail', args=[channelId]))

# Yield successive n-sized chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

# look for new videos of all channel from the XML feed
# scale terribly with the number of channel (regardless of how
# optimized your code is, the overhead of fetching a raw xml file still persists
# ). make it so it can run on small number of channels at a time.
# e.g. 5 channels per run
@display.controllers.debug_helper.st_time
def updateRecentFeedsAll(request):
    channels = Channel.objects.all()

    fetched = asyncio.run(fetchXML())
    newlyCrawledVideoIdList = []
    for item in fetched:
        newlyCrawledVideoIdList.extend(item)
    
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
    display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('index'))

async def updateRecentFeedsAllAsync(request):
    start_time = time.time()
    channels = await sync_to_async(Channel.objects.all)()
    channelIdList = []
    for channel in channels:
        channelIdList.append(channel.channelId)

    newlyCrawledVideoIdList = []
    tasks = []
    for channelId in channelIdList:
        task = asyncio.ensure_future(fetchRecentFeedsXMLAsync(channelId))
        tasks.append(task)
    results = await asyncio.gather(*tasks)

    for item in results:
        newlyCrawledVideoIdList.extend(item)
    
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
    
    display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    total = (time.time() - start_time)
    print('total: ', total)
    return HttpResponseRedirect(reverse('index'))

# Update the metadata of all upcoming and live video, use this to figure out if an upcoming
# live stream has started or otherwise, ongoing live stream has ended
@display.controllers.debug_helper.st_time
def updateWatchlistAll(request):
    watchlist = Video.objects.filter(Q(liveBroadcastContent='live') | Q(liveBroadcastContent='upcoming'))
    # in most cases, if you run this with enough interval, it shouldn't exceeds 50 videos. but just in case
    watchlistedVideoIdList = [video.videoId for video in watchlist]
    dividedChunks = list(divide_chunks(watchlistedVideoIdList, 50))

    for chunk in dividedChunks:
        videoIdString = ",".join(watchlistedVideoIdList)

        # what would happen if the video is unarchived or privated, who knows, too bad
        items = fetchVideosAPI(videoIdString)

        for item in items:
            currVideoId = item['id']
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

            currVideo = Video.objects.get(pk=currVideoId)
            currVideo.title = currTitle
            currVideo.thumbnail = currThumbnail
            currVideo.publishedAt = currPublishedAt
            currVideo.liveBroadcastContent = currLiveBroadcastContent
            currVideo.scheduledStartTime = currScheduledStartTime
            currVideo.actualStartTime = currActualStartTime
            currVideo.actualEndTime = currActualEndTime

            try:
                currVideo.save()
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('channel-index'))


    if len(watchlistedVideoIdList) > 0:
        messages.info(request, 'Watchlish updated. %d video(s) updated. %d YouTube API quota spent' % (len(watchlistedVideoIdList), display.controllers.debug_helper.API_CALLS_MADE))
        # don't forget to implement the message in the template
    else:
        messages.info(request, 'No new video found.')
        # don't forget to implement the message in the template
    display.controllers.debug_helper.API_CALLS_MADE_DAILY += display.controllers.debug_helper.API_CALLS_MADE
    display.controllers.debug_helper.API_CALLS_MADE = 0 # set it back to zero
    return HttpResponseRedirect(reverse('index'))
