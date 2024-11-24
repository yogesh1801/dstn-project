import logging
import os
from config import conf
from utility.get_kafka_producer import get_kafka_producer
import time
import re
import zlib

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_segment_number(segment_filename):
    match = re.search(r"segment_(\d+)\.ts", segment_filename)
    if match:
        return int(match.group(1))
    return None


def process_video_data():
    logger.info("Initializing Kafka producer...")
    producer = get_kafka_producer()

    running = True

    temp_dir = conf.OUTPUT_DIR
    processed_segments = set()
    while running:
        segments = sorted(os.listdir(temp_dir))

        for segment in segments:
            segment_number = get_segment_number(segment)
            if segment_number is None:
                continue

            segment_path = os.path.join(temp_dir, segment)

            if segment_number in processed_segments:
                continue

            with open(segment_path, "rb") as f:
                segment_data = f.read()

            key = str(segment_number).encode("utf-8")
            value = zlib.compress(segment_data, level=6)

            future = producer.send(conf.KAFKA_TOPIC, key=key, value=value)
            future.get(timeout=conf.KAFKA_TIMEOUT)

            logger.info(
                f"Sent segment {segment_number} " f"({len(segment_data) / 1024:.2f} KB)"
            )

            processed_segments.add(segment_number)
            # os.remove(segment_path)

        time.sleep(0.1)


if __name__ == "__main__":
    process_video_data()
