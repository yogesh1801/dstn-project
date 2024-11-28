import docker
import os
import logging
from config import conf

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Also log to console
    ],
)


class RAIDManager:
    def __init__(self, num_vms=conf.NUM_OF_VMS):
        self.docker_client = docker.from_env()
        self.num_vms = num_vms
        self.vms = []
        self.logger = logging.getLogger(__name__)  # Create a logger for the class

    def create_raid_vms(self):
        """
        Create Docker VMs for RAID 1 storage
        """
        self.logger.info(f"Creating {self.num_vms} RAID VMs...")
        try:
            for i in range(self.num_vms):
                vm_data_path = os.path.join(os.getcwd(), f"storage/raid_vm_{i}")
                self.logger.debug(f"Creating VM {i} with data path {vm_data_path}")
                vm = self.docker_client.containers.run(
                    "ubuntu:latest",
                    name=f"video-storage-vm-{i}",
                    volumes={vm_data_path: {"bind": "/mnt/storage", "mode": "rw"}},
                    detach=True,
                    command="tail -f /dev/null",  # Keep the container running
                )
                self.vms.append(vm)
                self.logger.info(f"VM {i} created successfully.")
        except Exception as e:
            self.logger.error(f"Error occurred while creating RAID VMs: {e}")

    def sync_data(self, source_path, destination_vms):
        """
        Sync data between VMs for RAID 1 mirroring

        :param source_path: Path of data to be synced
        :param destination_vms: List of destination VMs
        """
        self.logger.info(
            f"Syncing data from {source_path} to {len(destination_vms)} VMs..."
        )
        try:
            for dest_vm in destination_vms:
                self.logger.debug(f"Syncing to VM {dest_vm.name}...")
                dest_vm.exec_run(f"mkdir -p {os.path.dirname(source_path)}")
                self.docker_client.containers.get(dest_vm.id).exec_run(
                    f"cp -r {source_path} {os.path.dirname(source_path)}", user="root"
                )
                self.logger.info(f"Data synced successfully to VM {dest_vm.name}.")
        except Exception as e:
            self.logger.error(f"Error occurred during data sync: {e}")


if __name__ == "__main__":
    raid_manager = RAIDManager()
    raid_manager.create_raid_vms()
