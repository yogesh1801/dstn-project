from config import conf

def get_ffmpeg_cmd(input_source):

    input_format = conf.INPUT_FORMAT
    framerate = conf.FRAMERATE
    segment_duration = conf.SEGMENT_DURATION
    resolution = conf.RESOLUTION
    output_dir = conf.OUTPUT_DIR

    if input_format == 'v4l2':
        command = [
            'ffmpeg',
            '-f', 'v4l2',
            '-framerate', str(framerate),
            '-video_size', resolution,
            '-i', input_source,
            '-c:v', 'libx264',           # H.264 codec
            '-preset', 'ultrafast',       # Fastest encoding
            '-tune', 'zerolatency',      # Minimize latency
            '-profile:v', 'baseline',     # Basic H.264 profile for compatibility
            '-level', '3.0',             # H.264 level
            '-pix_fmt', 'yuv420p',       # Standard pixel format
            '-g', str(framerate * 2),    # GOP size (2 seconds)
            '-f', 'segment',             # Enable segmentation
            '-segment_time', str(segment_duration),
            '-segment_format', 'mpegts',
            '-segment_wrap', '30',       # Reuse segment files after 10 segments
            f'{output_dir}/segment_%d.ts'
        ]
    else:
        command = [
            'ffmpeg',
            '-i', input_source,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-profile:v', 'baseline',
            '-level', '3.0',
            '-pix_fmt', 'yuv420p',
            '-f', 'segment',
            '-segment_time', str(segment_duration),
            '-segment_format', 'mpegts',
            f'{output_dir}/segment_%d.ts'
        ]

    return command
