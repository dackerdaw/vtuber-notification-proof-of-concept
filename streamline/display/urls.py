from django.urls import path
from .controllers import render_controller

urlpatterns = [
    path('', render_controller.index, name='index'),
    path('channels/', render_controller.channelsIndex, name='channelsIndex'),
]