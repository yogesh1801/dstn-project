from config import conf
import time
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_batch_to_kafka(producer, batch):
    """
    Send a batch of messages to Kafka and return latencies
    """
    latencies = []
    for key, data in batch:
        start_send = time.time()
        future = producer.send(conf.KAFKA_TOPIC, key=key, value=data)
        try:
            future.get(timeout=conf.KAFKA_TIMEOUT)
            latency = time.time() - start_send
            latencies.append(latency)
            logger.info(f"Message sent with key {key}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
    return latencies
