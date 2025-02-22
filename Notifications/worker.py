import os
import django
from django.conf import settings
import httpx
import time
from typing import Optional
from datetime import datetime
from asgiref.sync import sync_to_async
import asyncio
import pytz
# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from message_service.models import Message, MessageStatus
from utils.logger import Logger

logger = Logger("worker")

TIME_ZONE = pytz.timezone(settings.TIME_ZONE)
WHATSAPP_ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_URL = settings.WHATSAPP_API_URL
WHATSAPP_PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID

API_URL = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

class Task:
    def __init__(self):
        self.running = True
        self.last_successful_run: Optional[datetime] = None

    async def _get_pending_messages(self, batch_size: int = 10, page: int = 1):
        try:
            pending_messages, next_page = await sync_to_async(Message.objects.get_pending_messages_by_priority)(
                page=page,
                batch_size=batch_size
            )
            return pending_messages, next_page
        except Exception as e:
            logger.error(f"Error getting pending messages: {e}")
            raise e
    
    def _make_message_body(self, message: Message):
        try:
            message_body = {
                "to": message.to_phone_number,
                "messaging_product": "whatsapp",
                "type": "template", 
                "template": message.rendered_message

            }
            return message_body

        except Exception as e:
            logger.error(f"Error making message body: {e}")
            raise e

    async def _send_message(self, message_body: dict) -> httpx.Response:
        max_retries = 5
        backoff_time = 1  # Start with 1 second
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending message: {message_body}")
                async with httpx.AsyncClient() as client:
                    response = await client.post(API_URL, headers=headers, json=message_body, timeout=30.0)
                    response.raise_for_status()
                    logger.info(f"Message sent successfully: {response.status_code}")
                    return response
            except (httpx.TimeoutException, httpx.HTTPError) as e:
                logger.error(f"Error sending message (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2, 60)  # Cap backoff time to 60 seconds
                else:
                    logger.error("Max retries reached Marking Message as Failed with error.")
                    return response

    async def process_messages(self, batch_size: int = 10):
        try:
            next_page: int = 1
            backoff_time = 1
            while self.running:
                # Get a batch of pending messages
                pending_messages,next_page = await self._get_pending_messages(batch_size=batch_size, page=next_page)
                logger.info(f"Fetched {len(pending_messages)} messages from page {next_page}.")

                if not pending_messages:
                    logger.info("No pending messages found. Sleeping for 5 seconds.")
                    await asyncio.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2,30)
                    continue
                
                backoff_time = 1
                logger.info(f"Pending messages: {pending_messages}")
                # Create a list to hold message bodies
                message_bodies = [self._make_message_body(message) for message in pending_messages]
                logger.info(f"Preparing to send {len(message_bodies)} messages.")
                logger.info(f"Message bodies: {message_bodies}")
                responses = await asyncio.gather(*(self._send_message(body) for body in message_bodies))
                
                for message, response in zip(pending_messages, responses):
                    if response.status_code == 200:
                        message.status = MessageStatus.SENT
                        message.sent_at = datetime.now(tz=TIME_ZONE)
                        logger.info(f"Message to {message.to_phone_number} sent successfully.")
                    else:
                        message.status = MessageStatus.FAILED
                        message.error_message = response.text
                        message.sent_at = datetime.now(tz=TIME_ZONE)
                        logger.error(f"Failed to send message to {message.to_phone_number}: {response.text}")
                    
                    await sync_to_async(message.save)()
                
                self.last_successful_run = datetime.now()
                logger.info("Batch processing completed. Sleeping for a while.")
                await asyncio.sleep(1 if next_page else 5)
            
            logger.info("Worker stopped gracefully.")
            
        except Exception as e:
            logger.error(f"Error polling database: {e}")
            raise e

if __name__ == '__main__':
    logger.info("Starting worker")
    worker = Task()
    try:
        asyncio.run(worker.process_messages(batch_size=10))
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Worker failed with error: {e}")
        raise
    finally:
        logger.info("Worker shutdown complete")