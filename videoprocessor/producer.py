import os
import threading
import time
import logging
from utility.get_kafka_producer import get_kafka_producer
import zlib
from config.conf import FOLDER_TOPIC_MAPPING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger()

running = True


def publish_video_segment(folder, topic):
    producer = get_kafka_producer()

    try:
        logger.info(
            f"Starting continuous monitoring of folder: {folder} for topic: {topic}"
        )
        folder_path = folder

        while running:
            try:
                for filename in os.listdir(folder_path):
                    if filename.endswith(".ts"):
                        file_path = os.path.join(folder_path, filename)
                        segment_name = os.path.splitext(filename)[0]

                        try:
                            with open(file_path, "rb") as file:
                                video_data = file.read()
                                key = segment_name.encode("utf-8")
                                value = zlib.compress(video_data, level=6)

                                future = producer.send(topic, key=key, value=value)
                                future.get(timeout=10)

                                logger.info(
                                    f"Published {filename} to topic {topic} with key {segment_name}"
                                )

                                os.remove(file_path)
                                logger.info(f"Deleted file: {filename}")

                        except Exception as e:
                            logger.error(f"Error processing file {filename}: {e}")
                            continue
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error while scanning folder {folder}: {e}")
                time.sleep(2)
    except Exception as e:
        logger.error(f"Fatal error in publisher thread for folder {folder}: {e}")
    finally:
        producer.flush()
        producer.close()
        logger.info(f"Producer closed for folder: {folder}")


def start_publishers():
    threads = []

    for folder, topic in FOLDER_TOPIC_MAPPING.items():
        if os.path.exists(folder):
            logger.info(f"Starting thread for folder: {folder}, topic: {topic}")
            thread = threading.Thread(
                target=publish_video_segment, args=(folder, topic)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
        else:
            logger.warning(f"Folder not found: {folder}")

    return threads


def graceful_shutdown(threads):
    global running
    running = False
    logger.info("Initiating graceful shutdown...")
    for thread in threads:
        thread.join()

    logger.info("All threads have been shut down.")


if __name__ == "__main__":
    try:
        threads = start_publishers()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break

    finally:
        graceful_shutdown(threads)
        logger.info("Program terminated.")
