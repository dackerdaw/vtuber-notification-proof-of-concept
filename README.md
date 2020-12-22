# vtuber-notification-proof-of-concept
A proof of concept of my implementation in fetching information for upcoming and live videos with 'minimal' performance and cost using YouTube XML feeds

In principle, this works by saving the channels of the talents in the database. When the channels were first saved, we also save all of their uploaded videos by making an api call for playlistItems of the channel 'Uploads' playlist and save every video from it. (one playlistItems.list() call costs 1 unit of YouTube API quota and can only execute 50 video items. e.g. channel with 200 videos will costs 200/50 = 4 units).

And from now on, that channel will be added to the watchlist. This watchlist will keep track of the YouTube XML feeds of all channels every 15 min and can provide real-time information about upcoming and live events of a channel with virtually zero costs (of course, making an xml fetch request in and of itself costs some overhead).

# Requirements
Available in requirements.txt. Alternatively, just run 'pip install -r requirements.txt' inside your virtualenv.
