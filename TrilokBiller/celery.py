import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Schedule: 11 PM IST is 17:30 UTC
app.conf.beat_schedule = {
    'daily-invoice-summary': {
        'task': 'accounts.tasks.send_invoice_summary_task',
        'schedule': crontab(hour=17, minute=30),
    },
}
