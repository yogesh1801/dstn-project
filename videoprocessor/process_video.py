import os
import zlib
import logging
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from utility.build_ffmpeg_command import build_ffmpeg_command
import subprocess
import shutil
from config import conf

logger = logging.getLogger(__name__)

QUALITY_PROFILES = [
    {"name": "720p", "bitrate": "2500k", "resolution": "1280:720"},
    {"name": "480p", "bitrate": "1000k", "resolution": "854:480"},
    {"name": "360p", "bitrate": "500k", "resolution": "640:360"},
]


def setup_directories(base_dir: str) -> Dict[str, str]:
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
    directories: Dict[str, str], segment_filename: str
) -> None:
    """Process a video segment into multiple quality profiles."""
    segment_number = os.path.splitext(segment_filename)[0].split('_')[-1]
    input_filename = os.path.join(directories["input"], segment_filename)

    try:
        for profile in QUALITY_PROFILES:
            transcode_segment(directories, segment_number, input_filename, profile)

    except Exception:
        logger.exception(f"Failed to process segment {segment_number}")


def process_directory(
    directory_path: str,
    directories: Dict[str, str],
    executor: ThreadPoolExecutor,
) -> None:
    """Process all video segments in the specified directory."""
    logger.info(f"Processing video segments from directory: {directory_path}")
    for segment_filename in sorted(os.listdir(directory_path)):
        if segment_filename.endswith(".ts"):
            shutil.copy(
                os.path.join(directory_path, segment_filename), directories["input"]
            )
            executor.submit(process_segment, directories, segment_filename)


def run_processor(base_dir: str, segment_dir: str) -> None:
    """Main function to run the video processor."""
    directories = setup_directories(base_dir)

    with ThreadPoolExecutor(max_workers=3) as executor:
        logger.info("Starting video processor...")
        process_directory(segment_dir, directories, executor)


def main() -> None:
    """Entry point for the video processor."""
    logging.basicConfig(level=logging.INFO)
    segment_directory = str(conf.INPUT_DIR)

    run_processor(
        base_dir=".",
        segment_dir=segment_directory,
    )


if __name__ == "__main__":
    main()