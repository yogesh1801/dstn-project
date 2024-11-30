import docker
import logging
import os
import threading
import time
import shutil
from datetime import datetime
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class FaultToleranceManager:
    """Manages fault tolerance for the RAID system."""
    
    def __init__(self, docker_client, monitor_interval: int = 30, max_retries: int = 3):
        self.docker_client = docker_client
        self.monitor_interval = monitor_interval
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self, vm_list: List[docker.models.containers.Container], 
                        vm_paths: List[str], primary_vm_index: int):
        """Start the fault tolerance monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return

        self.stop_event.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitor_vms,
            args=(vm_list, vm_paths, primary_vm_index),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Started fault tolerance monitoring")

    def stop_monitoring(self):
        """Stop the fault tolerance monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join(timeout=10)
            self.logger.info("Stopped fault tolerance monitoring")

    def _monitor_vms(self, vm_list: List[docker.models.containers.Container], 
                    vm_paths: List[str], primary_vm_index: int):
        """Monitor VMs health and recover failed VMs."""
        while not self.stop_event.is_set():
            try:
                for i, vm in enumerate(vm_list):
                    if i == primary_vm_index:
                        continue 
                        
                    try:
                        vm.reload()
                        if vm.status != 'running':
                            self.logger.warning(f"VM {vm.name} is not running (status: {vm.status})")
                            self._recover_vm(vm, vm_paths[i], vm_list, i)
                    except docker.errors.NotFound:
                        self.logger.error(f"VM {vm.name} not found, attempting recovery")
                        self._recover_vm(vm, vm_paths[i], vm_list, i)
                    except Exception as e:
                        self.logger.error(f"Error checking VM {vm.name}: {e}")

            except Exception as e:
                self.logger.error(f"Error in VM monitoring: {e}")
            finally:
                self.stop_event.wait(self.monitor_interval)

    def _recover_vm(self, failed_vm, vm_path: str, vm_list: List[docker.models.containers.Container], vm_index: int):
        """Recover a failed VM."""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                self.logger.info(f"Attempting to recover VM {failed_vm.name} (attempt {retry_count + 1})")
                
                # Remove the failed container
                try:
                    failed_vm.remove(force=True)
                except Exception as e:
                    self.logger.warning(f"Error removing failed container: {e}")

                # Create new container
                new_vm = self.docker_client.containers.run(
                    "ubuntu:latest",
                    name=failed_vm.name,
                    volumes={
                        vm_path: {
                            "bind": "/mnt/storage",
                            "mode": "rw"
                        }
                    },
                    detach=True,
                    command="/bin/bash -c 'apt-get update && apt-get install -y rsync && tail -f /dev/null'",
                    restart_policy={"Name": "unless-stopped"}
                )
                
                # Wait for container to be ready
                time.sleep(5)
                new_vm.reload()
                
                if new_vm.status == 'running':
                    vm_list[vm_index] = new_vm
                    self.logger.info(f"Successfully recovered VM {failed_vm.name}")
                    return True
                    
            except Exception as e:
                self.logger.error(f"Recovery attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                time.sleep(5)  # Wait before retry
                
        self.logger.error(f"Failed to recover VM {failed_vm.name} after {self.max_retries} attempts")
        return False


class RAIDManager:
    """Manages the RAID storage system with fault tolerance."""
    
    def __init__(self, num_vms: int = 3, sync_interval: int = 60, monitor_interval: int = 30):
        """
        Initialize RAIDManager with specified parameters.
        
        Args:
            num_vms (int): Number of VMs to create
            sync_interval (int): Interval in seconds between syncs
            monitor_interval (int): Interval in seconds between health checks
        """
        self.docker_client = docker.from_env()
        self.num_vms = num_vms
        self.sync_interval = sync_interval
        self.vms = []
        self.vm_paths = []
        self.primary_vm_index = 0
        self.sync_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self.last_sync: Dict[str, datetime] = {}
        self.sync_lock = threading.Lock()
        
        # Initialize fault tolerance manager
        self.fault_manager = FaultToleranceManager(
            docker_client=self.docker_client,
            monitor_interval=monitor_interval
        )

    def create_raid_vms(self):
        """Create Docker containers acting as VMs for storage and start processes."""
        try:
            self._cleanup_existing_vms()
            
            for i in range(self.num_vms):
                vm_data_path = os.path.abspath(os.path.join(os.getcwd(), f"storage/raid_vm_{i}"))
                os.makedirs(vm_data_path, exist_ok=True)
                self.vm_paths.append(vm_data_path)
                
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
                    command="/bin/bash -c 'apt-get update && apt-get install -y rsync && tail -f /dev/null'",
                    restart_policy={"Name": "unless-stopped"}
                )
                
                time.sleep(5)  # Wait for container setup
                
                self.vms.append(vm)
                self.last_sync[vm.name] = datetime.now()
                self.logger.info(f"VM {i} created successfully at {vm_data_path}")

            # Start background processes
            self._start_background_processes()
                
        except Exception as e:
            self.logger.error(f"Error creating RAID VMs: {e}")
            raise

    def _cleanup_existing_vms(self):
        """Remove any existing storage VMs."""
        try:
            containers = self.docker_client.containers.list(all=True)
            for container in containers:
                if container.name.startswith("video-storage-vm-"):
                    container.remove(force=True)
                    self.logger.info(f"Removed existing VM: {container.name}")
        except Exception as e:
            self.logger.error(f"Error cleaning up existing VMs: {e}")
            raise

    def _start_background_processes(self):
        """Start both sync and fault tolerance monitoring."""
        self._start_background_sync()
        self.fault_manager.start_monitoring(
            vm_list=self.vms,
            vm_paths=self.vm_paths,
            primary_vm_index=self.primary_vm_index
        )

    def _start_background_sync(self):
        """Start the background sync thread."""
        if self.sync_thread and self.sync_thread.is_alive():
            self.logger.warning("Sync thread is already running")
            return

        self.stop_event.clear()
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        self.logger.info(f"Started background sync (interval: {self.sync_interval}s)")

    def stop_all_processes(self):
        """Stop all background processes."""
        self.stop_sync()
        self.fault_manager.stop_monitoring()

    def stop_sync(self):
        """Stop the sync process gracefully."""
        if self.sync_thread and self.sync_thread.is_alive():
            self.stop_event.set()
            self.sync_thread.join(timeout=10)
            if self.sync_thread.is_alive():
                self.logger.warning("Sync thread did not stop gracefully")
            else:
                self.logger.info("Background sync stopped successfully")

    def _sync_worker(self):
        """Worker thread for continuous background sync operations."""
        while not self.stop_event.is_set():
            try:
                if len(self.vms) < 2:
                    self.logger.warning("Not enough VMs for sync")
                    self.stop_event.wait(self.sync_interval)
                    continue

                with self.sync_lock:
                    primary_path = self.vm_paths[self.primary_vm_index]
                    secondary_paths = [path for i, path in enumerate(self.vm_paths) 
                                    if i != self.primary_vm_index]
                    
                    self.sync_data(primary_path, secondary_paths)

            except Exception as e:
                self.logger.error(f"Error in sync worker: {e}")
            finally:
                self.stop_event.wait(self.sync_interval)

    def sync_data(self, source_path: str, destination_paths: List[str]):
        """
        Sync data from source path to destination paths using direct file system operations.
        
        Args:
            source_path (str): Source directory path
            destination_paths (list): List of destination directory paths
        """
        try:
            self.logger.info(f"Starting sync from {source_path}")
            
            for dest_path in destination_paths:
                try:
                    # Ensure directories exist
                    os.makedirs(dest_path, exist_ok=True)
                    
                    # Remove destination contents
                    for item in os.listdir(dest_path):
                        item_path = os.path.join(dest_path, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    
                    # Copy contents from source to destination
                    for item in os.listdir(source_path):
                        s = os.path.join(source_path, item)
                        d = os.path.join(dest_path, item)
                        if os.path.isfile(s):
                            shutil.copy2(s, d)
                        elif os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                    
                    self.last_sync[f"vm_{destination_paths.index(dest_path) + 1}"] = datetime.now()
                    self.logger.info(f"Sync completed successfully for {dest_path}")
                    
                except Exception as e:
                    self.logger.error(f"Error syncing to {dest_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error during sync process: {e}")

    def get_status(self) -> Dict[str, Dict]:
        """Get the current status of all VMs and processes."""
        status = {}
        for i, vm in enumerate(self.vms):
            try:
                vm.reload()
                status[vm.name] = {
                    'status': vm.status,
                    'is_primary': i == self.primary_vm_index,
                    'path': self.vm_paths[i],
                    'last_sync': self.last_sync.get(f"vm_{i}" if i > 0 else "primary"),
                    'sync_active': self.sync_thread is not None and self.sync_thread.is_alive(),
                    'fault_monitoring_active': self.fault_manager.monitor_thread is not None and 
                                            self.fault_manager.monitor_thread.is_alive()
                }
            except Exception as e:
                status[vm.name] = {
                    'status': 'error',
                    'error': str(e),
                    'path': self.vm_paths[i] if i < len(self.vm_paths) else 'unknown',
                    'sync_active': False,
                    'fault_monitoring_active': False
                }
        return status


if __name__ == "__main__":
    try:
        # Initialize RAID manager with 3 VMs
        raid_manager = RAIDManager(
            num_vms=3,             # Number of VMs to create
            sync_interval=60,       # Sync every 60 seconds
            monitor_interval=30     # Check VM health every 30 seconds
        )
        
        raid_manager.create_raid_vms()

        # Keep the main thread running
        while True:
            try:
                # Get and print status every 60 seconds
                status = raid_manager.get_status()
                print("\nCurrent Status:")
                for vm_name, vm_status in status.items():
                    print(f"\n{vm_name}:")
                    for key, value in vm_status.items():
                        print(f"  {key}: {value}")
                time.sleep(60)
            except KeyboardInterrupt:
                print("\nStopping RAID manager...")
                raid_manager.stop_all_processes()
                break

    except Exception as e:
        logging.error(f"Fatal error: {e}")