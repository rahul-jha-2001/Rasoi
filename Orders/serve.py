import threading
import os
from kafka_serve import KafkaServer
from grpc_serve import serve
import logging
from dotenv import load_dotenv




logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for most detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('order_service.log')  # Optional: log to file
    ]
)

logger.info(f"Enviroment Loaded {load_dotenv()}")


def run_kafka_server():
    """Starts the Kafka server."""
    try:
        kafka_server = KafkaServer()
        logger.info("Starting Kafka server...")
        kafka_server.run()
    except Exception as e:
        logger.error(f"Error in Kafka server: {e}")

def run_grpc_server():
    """Starts the gRPC server."""
    try:
        logger.info("Starting gRPC server...")
        serve()
    except Exception as e:
        logger.error(f"Error in gRPC server: {e}")

if __name__ == "__main__":
    # Create threads for gRPC and Kafka servers
    grpc_thread = threading.Thread(target=run_grpc_server, daemon=True)
    kafka_thread = threading.Thread(target=run_kafka_server, daemon=True)

    # Start the threads
    grpc_thread.start()
    kafka_thread.start()

    logger.info("Both gRPC and Kafka servers are running...")

    # Keep the main thread alive to listen for termination
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Shutting down services...")



    