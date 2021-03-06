from googleapiclient.discovery import build

import display.controllers.debug_helper

# don't forget to hide this key post-deployment
API_KEY = 'AIzaSyAL8iJZSXRd6iu-yhiMeu9osvMZX1XKjKE'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def fetchChannelAPI(channelId): # 1 unit per call
    api_request = youtube.channels().list(
        part="snippet,contentDetails",
        id=channelId
    )
    api_response = api_request.execute()
    display.controllers.debug_helper.API_CALLS_MADE += 1

    newId = api_response['items'][0]['id']
    newName = api_response['items'][0]['snippet']['title']
    newIcon = api_response['items'][0]['snippet']['thumbnails']['default']['url']
    newUploadPlaylist = api_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    return (newId, newName, newIcon, newUploadPlaylist)

def fetchPlaylistItemsAPI(playlistId):
    items = []
    nextPageToken=""
    while (nextPageToken != None):
        api_request = youtube.playlistItems().list( # 1 unit per call
            part="snippet",
            pageToken=nextPageToken,
            maxResults=50,
            playlistId=playlistId,
        )
        api_response = api_request.execute()
        display.controllers.debug_helper.API_CALLS_MADE += 1

        try:
            nextPageToken = api_response['nextPageToken']
            # print(nextPageToken)
        except:
            # print("This is the last page")
            nextPageToken=None
        items.extend(api_response['items'])

    return items

def fetchVideosAPI(videoId): # 1 unit per call, the maximum num of videoId in one call is 50 (separated by comma)

    api_request = youtube.videos().list(
        part="snippet,liveStreamingDetails",
        id=videoId
    )
    api_response = api_request.execute()
    display.controllers.debug_helper.API_CALLS_MADE += 1
    items = api_response['items']
    return items



