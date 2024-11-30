import threading
import time
import logging
import os
import docker
from config import conf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ],
)

class RAIDManager:
    def __init__(self, num_vms=conf.NUM_OF_VMS, sync_interval=60):
        """
        Initialize RAID Manager
        
        :param num_vms: Number of VMs to create (from config)
        :param sync_interval: Interval between syncs in seconds
        """
        self.docker_client = docker.from_env()
        self.num_vms = num_vms
        self.vms = []
        self.logger = logging.getLogger(__name__)
        self.sync_interval = sync_interval
        self.sync_thread = None
        self.primary_vm_index = conf.PRIMARY_STORAGE_VM_INT
        self.running = True

    def create_raid_vms(self):
        """
        Create Docker VMs for RAID 1 storage
        """
        self.logger.info(f"Creating {self.num_vms} RAID VMs...")
        try:
            self._cleanup_existing_vms()
            
            for i in range(self.num_vms):
                vm_data_path = os.path.join(os.getcwd(), f"storage/raid_vm_{i}")
                os.makedirs(vm_data_path, exist_ok=True) 
                
                self.logger.debug(f"Creating VM {i} with data path {vm_data_path}")
                
                vm = self.docker_client.containers.run(
                    "ubuntu:latest",
                    name=f"video-storage-vm-{i}",
                    volumes={
                        vm_data_path: {
                            "bind": "/mnt/storage",
                            "mode": "rw"
                        }
                    },
                    detach=True,
                    command="tail -f /dev/null", 
                    restart_policy={"Name": "unless-stopped"}
                )
                self.vms.append(vm)
                self.logger.info(f"VM {i} created successfully.")

        except Exception as e:
            self.logger.error(f"Error occurred while creating RAID VMs: {e}")
            raise

    def _cleanup_existing_vms(self):
        """
        Clean up any existing RAID VMs before creating new ones
        """
        try:
            containers = self.docker_client.containers.list(all=True)
            for container in containers:
                if container.name.startswith("video-storage-vm-"):
                    self.logger.info(f"Removing existing VM: {container.name}")
                    container.remove(force=True)
        except Exception as e:
            self.logger.error(f"Error cleaning up existing VMs: {e}")

    def start_periodic_sync(self):
        """
        Start a background thread for periodic data synchronization from primary VM to others
        """
        self.running = True
        self.sync_thread = threading.Thread(target=self._periodic_sync_worker, daemon=True)
        self.sync_thread.start()
        self.logger.info(f"Periodic synchronization started with interval {self.sync_interval} seconds")

    def _periodic_sync_worker(self):
        """
        Worker method to perform periodic synchronization from primary VM to others
        """
        while self.running:
            try:
                if not self.vms:
                    self.logger.warning("No VMs available for sync")
                    time.sleep(self.sync_interval)
                    continue

                primary_vm = self.vms[self.primary_vm_index]
                if not primary_vm:
                    self.logger.error("Primary VM not found")
                    time.sleep(self.sync_interval)
                    continue

                secondary_vms = [vm for vm in self.vms if vm != primary_vm]
                if not secondary_vms:
                    self.logger.warning("No secondary VMs available for sync")
                    time.sleep(self.sync_interval)
                    continue

                self.sync_data("/mnt/storage", secondary_vms, primary_vm)
                time.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in periodic sync: {e}")
                time.sleep(self.sync_interval)  # Wait before retrying

    def sync_data(self, source_path, destination_vms, source_vm=None):
        """
        Enhanced sync method to sync from primary VM to others
        
        :param source_path: Path of data to be synced
        :param destination_vms: List of destination VMs
        :param source_vm: Source VM to sync from (defaults to primary VM)
        """
        try:
            if source_vm is None:
                source_vm = self.vms[self.primary_vm_index]

            self.logger.info(
                f"Syncing data from primary VM ({source_vm.name}) to {len(destination_vms)} VMs..."
            )

            for dest_vm in destination_vms:
                if dest_vm == source_vm:
                    continue

                self.logger.debug(f"Syncing from {source_vm.name} to {dest_vm.name}...")
                
                # Ensure directories exist
                source_vm.exec_run(f"mkdir -p {os.path.dirname(source_path)}")
                dest_vm.exec_run(f"mkdir -p {os.path.dirname(source_path)}")

                source_cmd = f"tar -czf - -C {source_path} ."
                dest_cmd = f"docker exec -i {dest_vm.name} tar -xzf - -C {source_path}"
                result = source_vm.exec_run(f"{source_cmd} | {dest_cmd}", user="root")

                if result.exit_code != 0:
                    raise Exception(f"Sync failed with exit code {result.exit_code}: {result.output}")
                
                self.logger.info(f"Data synced successfully to VM {dest_vm.name}")

        except Exception as e:
            self.logger.error(f"Error occurred during data sync: {e}")
            raise

    def shutdown(self):
        """
        Clean shutdown of RAID manager and VMs
        """
        try:
            self.logger.info("Initiating RAID manager shutdown...")
            
            # Stop sync thread
            self.running = False
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)
                self.logger.info("Sync thread stopped")

            # Final sync before shutdown
            try:
                primary_vm = self.vms[self.primary_vm_index]
                secondary_vms = [vm for vm in self.vms if vm != primary_vm]
                self.sync_data("/mnt/storage", secondary_vms, primary_vm)
                self.logger.info("Final sync completed")
            except Exception as e:
                self.logger.error(f"Error during final sync: {e}")

            # Cleanup VMs
            for vm in self.vms:
                try:
                    self.logger.info(f"Stopping VM {vm.name}")
                    vm.stop()
                    vm.remove()
                    self.logger.info(f"VM {vm.name} removed")
                except Exception as e:
                    self.logger.error(f"Error cleaning up VM {vm.name}: {e}")

            self.logger.info("RAID manager shutdown completed")
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise

    def check_vm_status(self):
        """
        Check the status of all VMs
        Returns a dictionary with VM status information
        """
        status = {}
        try:
            for vm in self.vms:
                vm.reload()  # Refresh container info
                status[vm.name] = {
                    'status': vm.status,
                    'running': vm.status == 'running',
                    'is_primary': vm == self.vms[self.primary_vm_index]
                }
        except Exception as e:
            self.logger.error(f"Error checking VM status: {e}")
        return status   