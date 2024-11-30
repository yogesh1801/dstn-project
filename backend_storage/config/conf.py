import os

BASE_DIR = "storage/raid_vm_1"

DIRECTORIES = {
    "streams": os.path.join(BASE_DIR, "streams"),
    "metadata": os.path.join(BASE_DIR, "metadata"),
}

NUM_OF_VMS = 3

KAFKA_BROKER = "localhost:9092"
PRIMARY_STORAGE_VM_INT=0