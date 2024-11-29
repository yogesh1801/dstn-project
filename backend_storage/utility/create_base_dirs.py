from config import conf
import os
import shutil


def create_base_dirs():
    base_dir = conf.BASE_DIR
    shutil.rmtree(base_dir, ignore_errors=True)
    directories = conf.DIRECTORIES

    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
