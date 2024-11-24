import os
import zlib
import logging
from typing import Dict, List, Callable
from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaConsumer
from utility.setup_kafka_consumer import setup_kafka_consumer
from utility.build_ffmpeg_command import build_ffmpeg_command
import subprocess
from config import conf
import shutil

# Configure logging
logger = logging.getLogger(__name__)

# Constants for quality profiles
QUALITY_PROFILES = [
    {"name": "720p", "bitrate": "2500k", "resolution": "1280:720"},
    {"name": "480p", "bitrate": "1000k", "resolution": "854:480"},
    {"name": "360p", "bitrate": "500k", "resolution": "640:360"},
]


def setup_directories(base_dir: str) -> Dict[str, str]:
    """Create and return directory structure for video processing."""
    input_dir = os.path.join(base_dir, "input")
    profile_dirs = {
        profile["name"]: os.path.join(base_dir, profile["name"])
        for profile in QUALITY_PROFILES
    }

    shutil.rmtree(input_dir, ignore_errors=True)
    for dir_path in profile_dirs.values():
        shutil.rmtree(dir_path, ignore_errors=True)

    os.makedirs(input_dir, exist_ok=True)
    for dir_path in profile_dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    return {"input": input_dir, **profile_dirs}


def get_segment_path(
    directories: Dict[str, str], segment_number: str, profile_name: str = None
) -> str:
    """Generate file path for a segment."""
    directory = directories[profile_name] if profile_name else directories["input"]
    return os.path.join(directory, f"segment_{segment_number}.ts")


def transcode_segment(
    directories: Dict[str, str], segment_number: str, input_filename: str, profile: Dict
) -> None:
    """Transcode a segment to a specific quality profile using FFmpeg."""
    try:
        output_filename = get_segment_path(directories, segment_number, profile["name"])
        logger.info(f"Creating {profile['name']} version of segment {segment_number}")

        command = build_ffmpeg_command(input_filename, output_filename, profile)
        subprocess.run(command, check=True, capture_output=True)

        logger.info(
            f"Successfully created {profile['name']} version of segment {segment_number}"
        )
    except subprocess.CalledProcessError:
        logger.exception(
            f"FFmpeg transcoding failed for segment {segment_number}, profile {profile['name']}"
        )


def process_segment(
    directories: Dict[str, str], segment_number: str, compressed_data: bytes
) -> None:
    """Decompress and process a video segment into multiple quality profiles."""
    input_filename = None
    try:
        # Decompress the data
        input_data = zlib.decompress(compressed_data)
        logger.info(f"Decompressed segment {segment_number}")

        # Write input file
        input_filename = get_segment_path(directories, segment_number)
        with open(input_filename, "wb") as f:
            f.write(input_data)

        # Process each quality profile
        for profile in QUALITY_PROFILES:
            transcode_segment(directories, segment_number, input_filename, profile)

    except zlib.error:
        logger.exception(f"Failed to decompress segment {segment_number}")
    except Exception:
        logger.exception(f"Failed to process segment {segment_number}")
    finally:
        if input_filename and os.path.exists(input_filename):
            os.remove(input_filename)


def process_messages(
    consumer: KafkaConsumer,
    process_fn: Callable,
    executor: ThreadPoolExecutor,
    directories: Dict[str, str],
) -> None:
    """Process incoming Kafka messages."""
    try:
        for message in consumer:
            executor.submit(process_fn, directories, message.key, message.value)
    except KeyboardInterrupt:
        logger.info("Shutting down video processor...")
    finally:
        consumer.close()
        executor.shutdown(wait=True)


def run_processor(base_dir: str, bootstrap_servers: List[str], topic_name: str) -> None:
    """Main function to run the video processor."""
    directories = setup_directories(base_dir)
    consumer = setup_kafka_consumer(bootstrap_servers, topic_name)

    with ThreadPoolExecutor(max_workers=conf.MAX_WORKERS) as executor:
        logger.info("Starting video processor consumer...")
        process_messages(consumer, process_segment, executor, directories)


def main() -> None:
    """Entry point for the video processor."""
    logging.basicConfig(level=logging.INFO)

    run_processor(
        base_dir=".",
        bootstrap_servers=conf.INPUT_BOOTSTRAP_SERVER,
        topic_name=conf.INPUT_TOPIC,
    )


if __name__ == "__main__":
    main()
