import threading
from concurrent.futures import ThreadPoolExecutor
from .RAIDManager import RAIDManager
from .FaultManager import FaultToleranceManager
from .FaultManager import FaultToleranceMonitor

def kafka_consumer(topic, quality):
    consumer = KafkaConsumer(
        topic, 
        bootstrap_servers=[conf.KAFKA_BROKER], 
        group_id=f"video-storage-group-{quality}",
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )
    
    while True:
        try:
            message_batch = consumer.poll(timeout_ms=100)
            
            for _, messages in message_batch.items():
                for message in messages:
                    key = message.key.decode('utf-8')
                    
                    vars_array = key.split("_")
                    stream_id = vars_array[1]
                    segment_number = vars_array[2]
                    
                    create_stream_dirs(stream_id=stream_id)
                    save_video_segment(
                        stream_id=stream_id, 
                        quality=quality, 
                        segment_data=value, 
                        segment_number=segment_number
                    )
                    filename = f"segment_{segment_number}"
                    update_m3u8_file(
                        stream_id=stream_id, 
                        quality=quality, 
                        filename=filename
                    )
        except Exception as e:
            print(f"Error in consumer {quality}: {e}")
            continue

def run_quality_consumer(topic, quality):
    print(f"Starting consumer for quality: {quality}")
    kafka_consumer(topic, quality)

def backend_storage():
    create_base_dirs()

    raid_manager = RAIDManager(sync_interval=300)
    fault_tolerance_manager = FaultToleranceManager(raid_manager)
    
    raid_manager.create_raid_vms()
    raid_manager.start_periodic_sync()

    monitor_thread = FaultToleranceMonitor(
        raid_manager,
        fault_tolerance_manager,
    )
    
    monitor_thread.start()

    quality_configs = [
        ("1080p", "1080p"),
        ("720p", "720p"),
        ("480p", "480p"),
        ("360p", "360p")
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        for topic, quality in quality_configs:
            executor.submit(run_quality_consumer, topic, quality)

if __name__ == "__main__":
    try:
        backend_storage()
    except KeyboardInterrupt:
        print("Shutting down backend storage...")
    except Exception as e:
        print(f"Error in backend storage: {e}")