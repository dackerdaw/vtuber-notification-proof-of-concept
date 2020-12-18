# vtuber-notification-proof-of-concept
A proof of concept of my implementation in fetching information for upcoming and live videos with 'minimal' performance and cost using YouTube XML feeds

In principle, this works by saving the channels of the talents in the database. When the channels were first saved, we also save all of their uploaded videos by making an api call for playlistItems of the channel 'Uploads' playlist and save every video from it. (one playlistItems.list() call costs 1 unit of YouTube API quota and can only execute 50 video items. e.g. channel with 200 videos will costs 200/50 = 4 units).

And from now on, that channel will be added to the watchlist. This watchlist will keep track of the YouTube XML feeds of every channel and can provide real-time information about upcoming and live events of a channel with virtually zero costs (of course, making an xml fetch in and of itself request costs some overhead). What I'm aiming at is this watchlist will scan the xml feeds of every channel at certain periods of time per day (assuming the server keeps running of course). save new videos that are not registered in the database ad infinitum.

for this proof of concept, the watchlist will have to be executed manually from the home page for all channels or from the page of each channel. I have yet implemented a function that changes the state of an upcoming video to live when it's live or from a live video to an archived one when it's done.

# Requirements
Available in requirements.txt. Alternatively, just run 'pip install -r requirements.txt' inside your virtualenv.
