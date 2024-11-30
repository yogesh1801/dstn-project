import logging
import os
import re
from config import conf
from utility.get_kafka_producer import get_kafka_producer
import zlib

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def extract_segment_number(filename):
    """
    Extract the numeric part from filename in format segment_<stream_id>_int.ts
    Returns the integer for sorting, or 0 if no valid number is found
    """
    match = re.search(r'segment_\d+_(\d+)\.ts$', filename)
    return int(match.group(1)) if match else 0

def get_segment_base_name(segment_filename):
    """Extracts the segment name without the .ts extension."""
    return os.path.splitext(segment_filename)[0]

def process_video_data():
    logger.info("Initializing Kafka producer...")
    producer = get_kafka_producer()
    
    running = True
    
    temp_dir = conf.OUTPUT_DIR
    processed_segments = set()
    
    while running:
        # Filter .ts files and sort by the embedded integer
        segments = sorted(
            [seg for seg in os.listdir(temp_dir) if seg.endswith('.ts')],
            key=extract_segment_number
        )
        
        for segment in segments:
            segment_base_name = get_segment_base_name(segment)
            
            if segment_base_name in processed_segments:
                continue
            
            segment_path = os.path.join(temp_dir, segment)
            
            with open(segment_path, "rb") as f:
                segment_data = f.read()
            
            key = segment_base_name.encode("utf-8")
            value = zlib.compress(segment_data, level=6)
            
            future = producer.send(conf.KAFKA_TOPIC, key=key, value=value)
            future.get(timeout=conf.KAFKA_TIMEOUT)
            
            logger.info(
                f"Sent segment {segment_base_name} "
                f"({len(segment_data) / (1024*1024):.2f} MB)"
            )
            
            processed_segments.add(segment_base_name)
            os.remove(segment_path)

if __name__ == "__main__":
    process_video_data()