import time
import logging
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO or ERROR based on what level you want to log
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        #logging.FileHandler("fault_tolerance.log"),  # Log to a file
        logging.StreamHandler()  # Also log to console
    ]
)

class FaultToleranceManager:
    def __init__(self, raid_manager):
        self.raid_manager = raid_manager
        self.logger = logging.getLogger(__name__)  # Logger for this class

    def handle_vm_failure(self, failed_vm):
        """
        Handle VM failure and reconstruct data.

        :param failed_vm: Docker container of failed VM
        """
        self.logger.info(f"Handling failure for VM: {failed_vm.name}")

        try:
            failed_vm.remove(force=True)
            self.logger.debug(f"Removed failed VM: {failed_vm.name}")
            
            # Create a new VM for recovery
            new_vm = self.raid_manager.docker_client.containers.run(
                "ubuntu:latest",
                name="video-storage-vm-recovery",
                volumes={"/data/raid_vm_recovery": {"bind": "/mnt/storage", "mode": "rw"}},
                detach=True,
                command="tail -f /dev/null",
            )
            self.logger.info(f"Created new recovery VM: {new_vm.name}")

            # Sync data to the new VM
            self.raid_manager.sync_data("/mnt/storage", [new_vm])
            self.raid_manager.vms.append(new_vm)
            self.logger.info(f"Recovered VM: {new_vm.name}")
        except Exception as e:
            self.logger.error(f"Error during VM recovery: {e}")
            raise

class FaultToleranceMonitor(Thread):
    def __init__(self, raid_manager, fault_tolerance_manager, interval=10):
        super().__init__(daemon=True)
        self.raid_manager = raid_manager
        self.fault_tolerance_manager = fault_tolerance_manager
        self.interval = interval
        self.logger = logging.getLogger(__name__)  # Logger for this class

    def run(self):
        """Continuously monitor VMs for failures and handle recovery."""
        self.logger.info("Fault tolerance monitoring started.")
        try:
            while True:
                for vm in self.raid_manager.vms:
                    vm.reload()
                    if vm.status != "running":
                        self.logger.warning(f"Detected failure in VM: {vm.name}")
                        self.fault_tolerance_manager.handle_vm_failure(vm)
                time.sleep(self.interval)
        except Exception as e:
            self.logger.error(f"Error during VM monitoring: {e}")
        except KeyboardInterrupt:
            self.logger.info("VM monitoring stopped.")

