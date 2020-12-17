from django.urls import path
from .controllers import render_controller, confirm_controller

urlpatterns = [
    path('', render_controller.index, name='index'),
    path('channel/', render_controller.channelsIndex, name='channel-index'),
    path('channel/<str:channelId>/', render_controller.channelDetail, name='channel-detail'),
    path('channel/save/<str:channelId>/', confirm_controller.confirmSaveChannel, name='confirm-save-channel'),
    path('channel/update/feeds/<str:channelId>/', confirm_controller.updateRecentFeedsChannel, name='update-recent-feeds-channel'),
    path('update/feeds/', confirm_controller.updateRecentFeedsAll, name='update-recent-feeds-all'),
]