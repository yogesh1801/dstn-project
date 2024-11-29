from config import conf
import os


def update_m3u8_file(stream_id, quality, filename):
    directories = conf.DIRECTORIES
    playlist_path = os.path.join(
        directories["metadata"], f"stream_{stream_id}", f"{quality}.m3u8"
    )

    with open(playlist_path, "a") as f:
        f.write(f"#EXTINF:7.20000,\n{quality}/{filename}\n")
