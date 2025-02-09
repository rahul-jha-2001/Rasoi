import os
import django
from django.conf import settings
import httpx
import time
import signal
import threading
from typing import Optional
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from message_service.models import Message, MessageStatus
from utils.logger import Logger

logger = Logger("worker")

WHATSAPP_ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN
WHATSAPP_API_URL = settings.WHATSAPP_API_URL
WHATSAPP_PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID

# Create Redis connection
class Task:
    def __init__(self):
        self.running = True
        self.last_successful_run: Optional[datetime] = None
        self.health_check_port = settings.HEALTH_CHECK_PORT if hasattr(settings, 'HEALTH_CHECK_PORT') else 8080
        self._setup_signal_handlers()
        self._start_health_check_server()

    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping gracefully...")
        self.running = False

    def _start_health_check_server(self):
        """Start health check server in a separate thread"""
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    # Consider worker healthy if it has run successfully in the last minute
                    is_healthy = (
                        self.server.worker.last_successful_run is not None and 
                        (datetime.now() - self.server.worker.last_successful_run).seconds < 60
                    )
                    
                    if is_healthy:
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'healthy')
                    else:
                        self.send_response(503)
                        self.end_headers()
                        self.wfile.write(b'unhealthy')
                else:
                    self.send_response(404)
                    self.end_headers()

        server = HTTPServer(('', self.health_check_port), HealthCheckHandler)
        server.worker = self  # Attach worker instance to access last_successful_run
        
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"Health check server started on port {self.health_check_port}")

    def _get_pending_messages(self, batch_size: int = 10,page: int = 1):
        try:
            pending_messages, next_page = Message.objects.get_pending_messages_by_priority(
                page=page,
                batch_size=batch_size
            )
            if next_page:
                return pending_messages, next_page
            else:
                return pending_messages, None
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

    def _send_message(self, message: Message):
        try:
            API_URL = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            message_body = self._make_message_body(message)
            response = httpx.post(API_URL, headers=headers, json=message_body)
            if response.status_code == 200:
                message.status = MessageStatus.SENT
                message.save()
            else:
                message.status = MessageStatus.FAILED
                message.error_message = response.text
                message.save()
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise e

    def process_messages(self, batch_size: int = 10):
        try:
            next_page: int = 1
            while self.running:  # Check running flag in the loop
                pending_messages, next_page = self._get_pending_messages(batch_size=batch_size, page=next_page)
                
                if not pending_messages:
                    logger.info("No messages found, sleeping for 5 seconds")
                    time.sleep(5)  # Sleep for 5 seconds when no messages
                    continue
                    
                for message in pending_messages:
                    if not self.running:  # Check if we should stop processing
                        break
                    self._send_message(message)
                
                self.last_successful_run = datetime.now()
                
                if next_page:
                    logger.info(f"Processing next page: {next_page}")
                    time.sleep(1)  # Short delay between processing batches
                else:
                    logger.info("No more pages, sleeping for 5 seconds")
                    time.sleep(5)  # Longer delay when batch is complete
                    
            logger.info("Worker stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error polling database: {e}")
            raise e

if __name__ == '__main__':
    logger.info("Starting worker")
    worker = Task()
    try:
        worker.process_messages(batch_size=10)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Worker failed with error: {e}")
        raise
    finally:
        logger.info("Worker shutdown complete")