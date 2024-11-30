import os

PRIMARY_STORAGE_VM_INT=0
BASE_DIR = f"storage/raid_vm_{PRIMARY_STORAGE_VM_INT}"

DIRECTORIES = {
    "streams": os.path.join(BASE_DIR, "streams"),
    "metadata": os.path.join(BASE_DIR, "metadata"),
}

NUM_OF_VMS = 3

KAFKA_BROKER = "192.168.1.137:9092"