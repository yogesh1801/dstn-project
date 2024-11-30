import threading
from concurrent.futures import ThreadPoolExecutor
from utility.create_base_dirs import create_base_dirs
from utility.create_stream_dirs import create_stream_dirs
from utility.RAIDManager import RAIDManager
from utility.FaultManager import FaultToleranceManager, FaultToleranceMonitor
from utility.save_video_segement import save_video_segment
from utility.update_m3u8_file import update_m3u8_file
from kafka import KafkaConsumer
from config import conf
import logging
import signal
import sys
import os

# Global flags for graceful shutdown
shutdown_flag = threading.Event()
executor = None
raid_manager = None

logging.basicConfig(
    level=getattr(logging, conf.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger("signal_handler")
    signal_name = signal.Signals(signum).name
    logger.info(f"Received signal {signal_name}. Starting graceful shutdown...")
    
    shutdown_flag.set()
    
    # Stop the RAID manager if it exists
    global raid_manager
    if raid_manager:
        logger.info("Stopping RAID manager...")
        raid_manager.stop_all_processes()
    
    # Shutdown the thread pool executor if it exists
    global executor
    if executor:
        logger.info("Shutting down thread pool executor...")
        executor.shutdown(wait=True)
    
    logger.info("Graceful shutdown completed")
    sys.exit(0)

def kafka_consumer(topic, quality):
    logger = logging.getLogger(f"consumer.{quality}")
    consumer = KafkaConsumer(
        topic, 
        bootstrap_servers=[conf.KAFKA_BROKER], 
        group_id=f"video-storage-group-{quality}",
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )
    
    while not shutdown_flag.is_set():
        try:
            message_batch = consumer.poll(timeout_ms=100)
            
            if not message_batch:
                continue
                
            for _, messages in message_batch.items():
                if shutdown_flag.is_set():
                    break
                    
                for message in messages:
                    if shutdown_flag.is_set():
                        break
                        
                    key = message.key.decode('utf-8')
                    value = message.value
                    logger.info(f"processing {key}")
                    
                    vars_array = key.split("_")
                    stream_id = vars_array[1]
                    segment_number = vars_array[2]
                    
                    save_video_segment(
                        stream_id=stream_id, 
                        quality=quality, 
                        segment_data=value, 
                        segment_number=segment_number
                    )
                    filename = f"segment_{segment_number}.ts"
                    update_m3u8_file(
                        stream_id=stream_id, 
                        quality=quality, 
                        filename=filename
                    )
                    logger.debug(f"Processed segment {segment_number} for stream {stream_id}")
                    
        except Exception as e:
            if not shutdown_flag.is_set():
                logger.error(f"Error in consumer {quality}: {e}")
            continue
    
    # Clean up consumer
    try:
        consumer.close()
        logger.info(f"Kafka consumer for {quality} closed successfully")
    except Exception as e:
        logger.error(f"Error closing Kafka consumer for {quality}: {e}")

def run_quality_consumer(topic, quality):
    logger = logging.getLogger("consumer_runner")
    logger.info(f"Starting consumer for quality: {quality}")
    kafka_consumer(topic, quality)

def backend_storage():
    logger = logging.getLogger("backend_storage")
    logger.info("Initializing storage backend")
    
    global raid_manager, executor
    
    try:
        # Initialize RAID manager
        raid_manager = RAIDManager(
            num_vms=4,
            sync_interval=60,
            monitor_interval=30
        )
        
        # Create VMs and initialize directories
        raid_manager.create_raid_vms()
        create_base_dirs()
        logger.info("Fault tolerance monitoring started")
        
        # Configure quality settings
        quality_configs = [
            ("1080p", "1080p"),
            ("720p", "720p"),
            ("480p", "480p"),
            ("360p", "360p")
        ]
        
        # Start consumer threads
        executor = ThreadPoolExecutor(max_workers=4)
        futures = []
        
        for topic, quality in quality_configs:
            futures.append(executor.submit(run_quality_consumer, topic, quality))
            logger.info(f"Started consumer for {quality}")
        
        # Wait for shutdown signal
        shutdown_flag.wait()
        
    except Exception as e:
        logger.error(f"Error in backend storage initialization: {e}")
        raise
    finally:
        if executor:
            executor.shutdown(wait=True)
        if raid_manager:
            raid_manager.stop_all_processes()

def main():
    logger = logging.getLogger("main")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal
    signal.signal(signal.SIGINT, signal_handler)   # Handle interrupt signal (Ctrl+C)
    
    try:
        logger.info("Starting storage backend...")
        backend_storage()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()