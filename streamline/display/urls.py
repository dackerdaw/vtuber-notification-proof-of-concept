from django.urls import path
from .controllers import render_controller

urlpatterns = [
    path('', render_controller.index, name='index'),
]