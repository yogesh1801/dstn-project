import docker
from config import conf
import os


class RAIDManager:
    def __init__(self, num_vms=conf.NUM_OF_VMS):
        self.docker_client = docker.from_env()
        self.num_vms = num_vms
        self.vms = []

    def create_raid_vms(self):
        """
        Create Docker VMs for RAID 1 storage
        """
        for i in range(self.num_vms):
            vm_data_path = os.path.join(os.getcwd(), f"storage/raid_vm_{i}")
            vm = self.docker_client.containers.run(
                "ubuntu:latest",
                name=f"video-storage-vm-{i}",
                volumes={vm_data_path: {"bind": "/mnt/storage", "mode": "rw"}},
                detach=True,
                command="tail -f /dev/null",
            )
            self.vms.append(vm)

    def sync_data(self, source_path, destination_vms):
        """
        Sync data between VMs for RAID 1 mirroring

        :param source_path: Path of data to be synced
        :param destination_vms: List of destination VMs
        """
        for dest_vm in destination_vms:
            dest_vm.exec_run(f"mkdir -p {os.path.dirname(source_path)}")
            self.docker_client.containers.get(dest_vm.id).exec_run(
                f"cp -r {source_path} {os.path.dirname(source_path)}", user="root"
            )


if __name__ == "__main__":
    raid_manager = RAIDManager()
    raid_manager.create_raid_vms()
