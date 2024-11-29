from config import conf
import os
from .create_stream_dirs import create_stream_dirs


def save_video_segment(stream_id, quality, segment_data, segment_number):
    directories = conf.DIRECTORIES

    stream_path = os.path.join(directories["streams"], f"stream_{stream_id}")

    if os.path.exists(stream_path):
        create_stream_dirs(stream_id=stream_id)

    filename = f"segement_{segment_number}"

    segment_path = os.path.join(stream_path, quality, filename)
    with open(segment_path, "wb") as f:
        f.write(segment_data)
