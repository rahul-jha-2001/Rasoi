import schedule
import time
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template

from utils.logger import Logger

logger = Logger("cron_job")


def sync_templates():
    logger.info("Starting sync templates")
    Template.objects.sync_with_whatsapp()
    logger.info("Sync templates completed")



if __name__ == "__main__":
    schedule.every(1).hours.do(sync_templates)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Cron job stopped by user.")
