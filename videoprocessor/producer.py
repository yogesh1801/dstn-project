import os
import threading
from kafka import KafkaProducer
import time
import logging
from config import KAFKA_CONFIG, FOLDER_TOPIC_MAPPING, INPUT_DIR  # Import the config

# Set up logger
logging.basicConfig(level=logging.INFO,  # Set the logging level
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("video_segment_publisher.log"),  # Log to file
                        logging.StreamHandler()  # Also log to console
                    ])
logger = logging.getLogger()

# Create a Kafka producer instance using the config from config.py
producer = KafkaProducer(
    bootstrap_servers=KAFKA_CONFIG['bootstrap.servers'],
    client_id=KAFKA_CONFIG['client.id'],
    key_serializer=lambda x: x.encode('utf-8'),  # Serialize key as UTF-8 string
    value_serializer=lambda x: x  # The video data is already in bytes
)

# Function to read files from the folder and publish them to the appropriate Kafka topic
def publish_video_segment(folder, topic):
    try:
        logger.info(f"Starting to publish video segments from folder: {folder} to topic: {topic}")
        folder_path = os.path.join(INPUT_DIR, folder)
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.ts'):
                file_path = os.path.join(folder_path, filename)
                
                # Extract key as the name of the segment without the .ts extension
                segment_name = os.path.splitext(filename)[0]
                
                # Read the video segment
                with open(file_path, 'rb') as file:
                    video_data = file.read()
                    
                    # Publish to Kafka with the segment name as the key
                    producer.send(
                        topic,
                        key=segment_name,
                        value=video_data
                    )
                    logger.info(f"Published {filename} to topic {topic} with key {segment_name}")
                
                # Simulate a delay between publishing chunks
                time.sleep(1)  
    except Exception as e:
        logger.error(f"Error while publishing from folder {folder}: {e}")

# Multithreading to handle each folder-topic pair
def start_publishers():
    threads = []
    
    for folder, topic in FOLDER_TOPIC_MAPPING.items():  # Use config for folders and topics
        if os.path.exists(os.path.join(INPUT_DIR, folder)):
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
    
    # Close the producer connection
    producer.close()
    logger.info("Producer closed.")
