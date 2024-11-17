import logging
import os
import subprocess
from config import conf
from utility.get_ffmpeg_cmd import get_ffmpeg_cmd
import shutil

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_ffmpeg():
    temp_dir = conf.OUTPUT_DIR
    logger.info(f"Creating temp dir: {temp_dir}")
    shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    input_source = conf.INPUT_VIDEO_SOURCE
    logger.info(f"Starting video capture from {input_source}")

    ffmpeg_cmd = get_ffmpeg_cmd(input_source=input_source)
    logger.info(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")

    try:
        # Run the ffmpeg command and inherit stdout/stderr from the parent shell
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=None,  # Use parent stdout
            stderr=None,  # Use parent stderr
            text=True,  # Ensures proper text handling
        )

        process.wait()  # Wait for the process to complete

        if process.returncode == 0:
            logger.info("FFmpeg command executed successfully.")
        else:
            logger.error(f"FFmpeg failed with return code {process.returncode}.")
    except Exception as e:
        logger.error(f"Error while running FFmpeg: {e}")


if __name__ == "__main__":
    run_ffmpeg()
