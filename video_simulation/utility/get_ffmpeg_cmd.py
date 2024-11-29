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
            "hls",
            "-hls_time",
            str(segment_duration),
            "-hls_list_size",
            "0",                    # Keep all segments in playlist
            "-hls_segment_type",
            "mpegts",
            "-hls_segment_filename",
            f"{output_dir}/segment_{stream_id}_%d.ts",
            f"{output_dir}/playlist.m3u8",
        ]
    else:
        command = [
            "ffmpeg",
            "-threads", 
            "0",
            "-i",
            input_source,
            "-map",
            "0:v:0",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-copyts",
            "-avoid_negative_ts",
            "make_zero",
            "-max_muxing_queue_size",
            "1024",
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
            "hls",
            "-hls_time",
            str(segment_duration),
            "-hls_list_size",
            "0",                    # Keep all segments in playlist
            "-hls_segment_type",
            "mpegts",
            "-hls_segment_filename",
            f"{output_dir}/segment_{stream_id}_%d.ts",
            f"{output_dir}/playlist.m3u8",
        ]
    
    return command