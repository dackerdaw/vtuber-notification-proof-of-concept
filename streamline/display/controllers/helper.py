from display.models.channel import Channel
from display.models.video import Video

from .youtube_xml_feed import fetchXML
from .youtube_api_calls import fetchVideosAPI

# Yield successive n-sized chunks from l. 
def divide_chunks(l, n): 
      
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]

def refreshFeeds():
    fetched = fetchXML()
    newlyCrawledVideoIdList = []
    for item in fetched:
        newlyCrawledVideoIdList.extend(item)
    
    # YouTube API videos.list() allows up to 50 videoIds per call.
    # since we crawl all channels periodically, it shouldn't exceeds 50.
    # but for testing purposes, we might crawl all channels that has never been 
    # crawled which potentially yields more than 50 uncrawled videos
    numOfVids = len(newlyCrawledVideoIdList)
    print(numOfVids)

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
        return numOfVids
    else:
        return 0