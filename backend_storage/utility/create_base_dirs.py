from config import conf
import os

def create_base_dirs():
    base_dir = conf.BASE_DIR
    directories = conf.DIRECTORIES

    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
