import os
import threading
from confluent_kafka import Producer
import time
import logging
from config import KAFKA_CONFIG, FOLDER_TOPIC_MAPPING  # Import the config

# Set up logger
logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("video_segment_publisher.log"),  # Log to file
                        logging.StreamHandler()  # Also log to console
                    ])
logger = logging.getLogger()

# Create a Kafka producer instance using the config from config.py
producer = Producer(KAFKA_CONFIG)

# Function to read files from the folder and publish them to the appropriate Kafka topic
def publish_video_segment(folder, topic):
    try:
        logger.info(f"Starting to publish video segments from folder: {folder} to topic: {topic}")
        for filename in os.listdir(folder):
            if filename.endswith('.ts'):
                file_path = os.path.join(folder, filename)
                
                # Extract key as the name of the segment without the .ts extension
                segment_name = os.path.splitext(filename)[0]
                
                # Read the video segment
                with open(file_path, 'rb') as file:
                    video_data = file.read()
                    
                    # Publish to Kafka with the segment name as the key
                    producer.produce(
                        topic=topic,
                        key=segment_name,
                        value=video_data,
                        callback=delivery_report
                    )
                    logger.info(f"Published {filename} to topic {topic} with key {segment_name}")
                
                # Poll the producer to deliver messages
                producer.poll(0)
                
                time.sleep(1)  # Simulate a delay between publishing chunks
    except Exception as e:
        logger.error(f"Error while publishing from folder {folder}: {e}")

# Delivery report callback
def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Multithreading to handle each folder-topic pair
def start_publishers():
    threads = []
    
    for folder, topic in FOLDER_TOPIC_MAPPING.items():  # Use config for folders and topics
        if os.path.exists(folder):
            # Create and start a new thread for each folder-topic pair
            logger.info(f"Starting thread for folder: {folder}, topic: {topic}")
            thread = threading.Thread(target=publish_video_segment, args=(folder, topic))
            thread.start()
            threads.append(thread)
        else:
            logger.warning(f"Folder {folder} does not exist.")
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    logger.info("All threads have completed publishing.")

if __name__ == '__main__':
    # Start publishing video segments to Kafka
    start_publishers()
    
    # Flush any remaining messages in the producer
    producer.flush()
    logger.info("Producer flush completed.")
