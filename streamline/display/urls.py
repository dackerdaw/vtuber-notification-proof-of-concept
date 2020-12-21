from django.urls import path
from .controllers import render_controller, confirm_controller, jajal

urlpatterns = [
    path('', render_controller.index, name='index'),
    path('channel/', render_controller.channelsIndex, name='channel-index'),
    path('channel/<str:channelId>/', render_controller.channelDetail, name='channel-detail'),
    path('channel/save/<str:channelId>/', confirm_controller.confirmSaveChannel, name='confirm-save-channel'),
    path('channel/update/feeds/<str:channelId>/', confirm_controller.updateRecentFeedsChannel, name='update-recent-feeds-channel'),
    path('channel/update/watchlist/<str:channelId>/', confirm_controller.updateWatchlistChannel, name='update-watchlist-channel'),
    path('update/feeds/', confirm_controller.updateRecentFeedsAllAsync, name='update-recent-feeds-all'),
    path('update/watchlist/', confirm_controller.updateWatchlistAll, name='update-watchlist-all'),

    path('jajal/', jajal.utama, name='jajal'),
]