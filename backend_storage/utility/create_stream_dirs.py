import os
from config import conf

def create_stream_dirs(self, stream_id):
    directories = conf.DIRECTORIES
    stream_path = os.path.join(directories['streams'], f'stream_{stream_id}')
    metadata_path = os.path.join(directories['metadata'], f'stream_{stream_id}')

    qualities = ['1080p', '720p', '480p', '360p']

    for quality in qualities:
        os.makedirs(os.path.join(stream_path, quality), exist_ok=True)

    for quality in qualities:
        with open(os.path.join(metadata_path, f'{quality}.m3u8'), 'w') as f:
            f.write("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:5\n#EXT-X-MEDIA-SEQUENCE:0")


