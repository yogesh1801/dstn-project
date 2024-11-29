# backend_storage/RAIDManager.py
import docker

class RAIDManager:
    def __init__(self, docker_client, num_vms=3):
        self.docker_client = docker_client
        self.num_vms = num_vms
        self.vms = []
        
    def create_raid_vms(self):
        """
        Create Docker VMs for RAID 1 storage
        """
        for i in range(self.num_vms):
            vm = self.docker_client.containers.run(
                'ubuntu:latest',
                name=f'video-storage-vm-{i}',
                volumes={
                    f'/data/raid_vm_{i}': {'bind': '/mnt/storage', 'mode': 'rw'}
                },
                detach=True,
                command='tail -f /dev/null'  # Keep container running
            )
            self.vms.append(vm)
    
    def sync_data(self, source_path, destination_vms):
        """
        Sync data between VMs for RAID 1 mirroring
        
        :param source_path: Path of data to be synced
        :param destination_vms: List of destination VMs
        """
        for dest_vm in destination_vms:
            # Use docker cp to copy files between containers
            dest_vm.exec_run(f'mkdir -p {os.path.dirname(source_path)}')
            self.docker_client.containers.get(dest_vm.id).exec_run(
                f'cp -r {source_path} {os.path.dirname(source_path)}',
                user='root'
            )
