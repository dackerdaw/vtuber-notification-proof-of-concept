from celery import shared_task
from celery.schedules import crontab

from django.core.mail import send_mail

from .controllers.helper import refreshFeeds, refreshWatchlist

@shared_task 
def refreshFeedsBackground():
    result = refreshFeeds()
    print('%d new video(s) crawled' % result)

@shared_task 
def refreshWatchlistBackground():
    result = refreshWatchlist()
    print('%d video(s) refreshed' % result)

@shared_task
def send_email_task():
    send_mail(
        'Celery task worked!',
        'This is proof that the task worked!',
        'ibrahim.qardhawi@student.president.ac.id',
        ['haxec75817@nenekbet.com']
    )

    return None

