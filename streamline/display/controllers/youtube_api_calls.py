from googleapiclient.discovery import build

API_KEY = 'AIzaSyAL8iJZSXRd6iu-yhiMeu9osvMZX1XKjKE'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def fetchChannelAPI(channelId):
    api_request = youtube.channels().list(
        part="snippet,contentDetails",
        id=channelId
    )

    api_response = api_request.execute()
    newId = api_response['items'][0]['id']
    newName = api_response['items'][0]['snippet']['title']
    newIcon = api_response['items'][0]['snippet']['thumbnails']['default']['url']
    newUploadPlaylist = api_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    return (newId, newName, newIcon, newUploadPlaylist)