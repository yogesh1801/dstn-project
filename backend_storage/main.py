from config import conf

from utility.create_base_dirs import create_base_dirs
from utility.create_stream_dirs import create_stream_dirs


def backend_storage():
    create_base_dirs()
    create_stream_dirs('yogesh')


if __name__ == "__main__":
    backend_storage()
