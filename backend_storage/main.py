# main.py
from config import conf
from utility.create_base_dirs import create_base_dirs
from utility.create_stream_dirs import create_stream_dirs
from docker import DockerClient

# Adjusted imports for RAIDManager, VideoChunkManager, KafkaVideoConsumer, FaultToleranceManager
from backend_storage.raid_manager import RAIDManager
from backend_storage.video_chunk_manager import VideoChunkManager
from backend_storage.KafkaVideoConsumer import KafkaVideoConsumer
from backend_storage.fault_tolerance import FaultToleranceManager, FaultToleranceMonitor

def backend_storage():
    # Create base and stream directories
    create_base_dirs()
    create_stream_dirs('yogesh')  # Assuming 'yogesh' is the stream ID for testing

    # Initialize Docker client and managers for RAID and fault tolerance
    docker_client = DockerClient(base_url="unix://var/run/docker.sock")
    raid_manager = RAIDManager(docker_client)
    fault_tolerance_manager = FaultToleranceManager(raid_manager)
    video_chunk_manager = VideoChunkManager()

    # Create RAID VMs (simulating RAID storage system)
    raid_manager.create_raid_vms()

    # Start Fault Tolerance Monitoring
    monitor_thread = FaultToleranceMonitor(raid_manager, fault_tolerance_manager, interval=10)
    monitor_thread.start()

    # Start Kafka video chunk consumer
    kafka_consumer = KafkaVideoConsumer(
        bootstrap_servers=["localhost:9092"],
        topic="video_chunks",
        video_chunk_manager=video_chunk_manager,
    )
    kafka_consumer.consume_video_chunks()


if __name__ == "__main__":
    backend_storage()
