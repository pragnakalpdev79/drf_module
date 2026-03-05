import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.conf.broker_transport_options = {"visbility_timeout": 3600 }
app.conf.result_backend_transport_options = {'retry_on_timeout':True,'socket_timeout':300}
app.autodiscover_tasks()
