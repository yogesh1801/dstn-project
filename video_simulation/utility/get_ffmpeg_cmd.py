from config import conf


def get_ffmpeg_cmd(input_source, stream_id):
    input_format = conf.INPUT_FORMAT
    framerate = conf.FRAMERATE
    segment_duration = conf.SEGMENT_DURATION
    resolution = conf.RESOLUTION
    output_dir = conf.OUTPUT_DIR

    if input_format == "v4l2":
        command = [
            "ffmpeg",
            "-threads",
            "0",
            "-f",
            "v4l2",
            "-framerate",
            str(framerate),
            "-video_size",
            resolution,
            "-i",
            input_source,
            "-map",
            "0:v:0",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-pix_fmt",
            "yuv420p",
            "-g",
            str(framerate * 2),
            "-f",
            "segment",
            "-segment_time",
            str(segment_duration),
            "-segment_format",
            "mpegts",
            "-segment_wrap",
            "24",
            "-reset_timestamps",
            "1",
            f"{output_dir}/segment_%d.ts",
        ]
    else:
        command = [
            "ffmpeg",
            "-threads",
            "0",
            "-i",
            input_source,
            "-map",
            "0:v:0",  # Ensure we're getting the video stream
            "-c:v",
            "libx264",  # Use H.264 codec
            "-preset",
            "ultrafast",  # Fastest encoding
            "-copyts",  # Copy timestamps for accurate splitting
            "-avoid_negative_ts",
            "make_zero",  # Avoid negative timestamps
            "-max_muxing_queue_size",
            "1024",  # Increase muxing queue for large file
            "-tune",
            "zerolatency",
            "-profile:v",
            "baseline",
            "-level",
            "3.0",
            "-pix_fmt",
            "yuv420p",
            "-g",
            str(framerate * 2),
            "-f",
            "segment",
            "-segment_time",
            str(segment_duration),  # 4 second segments
            "-segment_format",
            "mpegts",
            "-reset_timestamps",
            "1",  # Reset timestamps at start of each segment
            f"{output_dir}/segment_{stream_id}_%d.ts",
        ]

    return command
