import os
import logging
from typing import Dict
from utility.build_ffmpeg_command import build_ffmpeg_command
import subprocess
from config import conf
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import shutil
import time

logger = logging.getLogger(__name__)

# Define quality profiles
QUALITY_PROFILES = [
    {"name": "1080p", "bitrate": "5000k", "resolution": "1920:1080"},
    {"name": "720p", "bitrate": "2500k", "resolution": "1280:720"},
    {"name": "480p", "bitrate": "1000k", "resolution": "854:480"},
    {"name": "360p", "bitrate": "500k", "resolution": "640:360"},
]


def setup_directories(base_dir: str) -> Dict[str, str]:
    """Create directories for quality profiles."""
    profile_dirs = {
        profile["name"]: os.path.join(base_dir, profile["name"])
        for profile in QUALITY_PROFILES
    }

    # Clean and recreate directories
    for dir_path in profile_dirs.values():
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path, exist_ok=True)

    return profile_dirs


def transcode_segment(
    directories: Dict[str, str], segment_filename: str, segment_path: str, profile: Dict
) -> None:
    """Transcode a segment to a specific quality profile using FFmpeg."""
    try:
        output_filename = os.path.join(directories[profile["name"]], segment_filename)
        logger.info(f"Creating {profile['name']} version of segment {segment_filename}")

        command = build_ffmpeg_command(segment_path, output_filename, profile)
        subprocess.run(command, check=True, capture_output=True)

        logger.info(
            f"Successfully created {profile['name']} version of segment {segment_filename}"
        )
    except subprocess.CalledProcessError:
        logger.exception(
            f"FFmpeg transcoding failed for segment {segment_filename}, profile {profile['name']}"
        )


def process_segment(
    directories: Dict[str, str], segment_filename: str, segment_path: str
) -> None:
    """Process a video segment into multiple quality profiles using multithreading."""
    try:
        with ThreadPoolExecutor(max_workers=len(QUALITY_PROFILES)) as executor:
            # Submit all quality profile tasks
            futures = [
                executor.submit(
                    transcode_segment, directories, segment_filename, segment_path, profile
                )
                for profile in QUALITY_PROFILES
            ]

            # Wait for all threads to complete
            wait(futures, return_when=ALL_COMPLETED)

        # Delete the original segment after all profiles are processed
        os.remove(segment_path)
        logger.info(f"Deleted original segment: {segment_path}")

    except Exception:
        logger.exception(f"Failed to process segment {segment_filename}")


def process_directory(directory_path: str, directories: Dict[str, str]) -> None:
    """Process all video segments in the specified directory sequentially."""
    logger.info(f"Processing video segments from directory: {directory_path}")
    for segment_filename in sorted(os.listdir(directory_path)):
        if segment_filename.endswith(".ts"):
            segment_path = os.path.join(directory_path, segment_filename)
            process_segment(directories, segment_filename, segment_path)


def run_processor(base_dir: str, segment_dir: str) -> None:
    """Main function to run the video processor."""
    directories = setup_directories(base_dir)
    logger.info("Starting video processor...")

    # Continuous running process to check and process segments
    while True:
        logger.info("Checking for new video segments...")
        # Check if there are any new segments
        if any(f.endswith(".ts") for f in os.listdir(segment_dir)):
            process_directory(segment_dir, directories)
        else:
            logger.info("No new segments found. Waiting for new segments.")

        # Wait before checking again (adjust as needed)
        time.sleep(5)


def main() -> None:
    """Entry point for the video processor."""
    logging.basicConfig(level=logging.INFO)
    segment_directory = str(conf.INPUT_DIR)

    run_processor(
        base_dir=".",  # Directory for storing transcoded files
        segment_dir=segment_directory,  # Directory containing the input video segments
    )


if __name__ == "__main__":
    main()
