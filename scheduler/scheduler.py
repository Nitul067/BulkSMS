import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from .whatsapp import send_message


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def start():
    if settings.DEBUG:
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler.add_job(send_message, "cron", id="message", 
                      minute=30, hour=17, day_of_week="mon-sat", 
                      replace_existing=True)

    scheduler.start()

