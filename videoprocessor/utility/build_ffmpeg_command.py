from typing import Dict, List


def get_bitrate_value(bitrate: str) -> int:
    """Extract numeric value from bitrate string."""
    return int(bitrate.replace("k", ""))


def build_ffmpeg_command(input_file: str, output_file: str, profile: Dict) -> List[str]:
    """
    Build FFmpeg command for video transcoding.

    Args:
        input_file (str): Path to the input video file
        output_file (str): Path where the transcoded video will be saved
        profile (Dict): Quality profile containing bitrate and resolution settings

    Returns:
        List[str]: FFmpeg command as a list of string arguments
    """
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-b:v",
        profile["bitrate"],
        "-bufsize",
        f'{get_bitrate_value(profile["bitrate"]) * 2}k',
        "-vf",
        f'scale={profile["resolution"]}',
        "-y",
        output_file,
    ]
