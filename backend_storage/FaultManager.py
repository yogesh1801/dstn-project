import time
import logging
from threading import Thread

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  
    ],
)

class FaultToleranceManager:
    def __init__(self, raid_manager):
        self.raid_manager = raid_manager
        self.logger = logging.getLogger(__name__)

    def handle_vm_failure(self, failed_vm):
        """
        Handle VM failure and reconstruct data.

        :param failed_vm: Docker container of failed VM
        """
        self.logger.info(f"Handling failure for VM: {failed_vm.name}")

        try:
            failed_vm.remove(force=True)
            self.logger.debug(f"Removed failed VM: {failed_vm.name}")

            vm_data_path = os.path.join(os.getcwd(), f"storage/raid_vm_recovery")
            new_vm = self.raid_manager.docker_client.containers.run(
                "ubuntu:latest",
                name="video-storage-vm-recovery",
                volumes={
                    vm_data_path: {"bind": "/mnt/storage", "mode": "rw"}
                },
                detach=True,
                command="tail -f /dev/null",
            )
            self.logger.info(f"Created new recovery VM: {new_vm.name}")

            self.raid_manager.sync_data("/mnt/storage", [new_vm])
            self.raid_manager.vms.append(new_vm)
            self.logger.info(f"Recovered VM: {new_vm.name}")
        except Exception as e:
            self.logger.error(f"Error during VM recovery: {e}")
            raise


class FaultToleranceMonitor(Thread):
    def __init__(self, raid_manager, fault_tolerance_manager, interval=10, max_retries=3):
        super().__init__(daemon=True)
        self.raid_manager = raid_manager
        self.fault_tolerance_manager = fault_tolerance_manager
        self.interval = interval
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        self.failed_vm_retries = {}

    def run(self):
        """
        Advanced VM monitoring with retry and logging mechanism
        """
        self.logger.info("Advanced fault tolerance monitoring started.")
        try:
            while True:
                self._monitor_vms()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.logger.info("VM monitoring stopped.")
        except Exception as e:
            self.logger.error(f"Catastrophic error in monitoring: {e}")

    def _monitor_vms(self):
        """
        Detailed VM monitoring with advanced failure handling
        """
        for vm in self.raid_manager.vms:
            try:
                vm.reload()
                
                if vm.status != "running":
                    self._handle_vm_failure(vm)
                else:
                    if vm.name in self.failed_vm_retries:
                        del self.failed_vm_retries[vm.name]

            except Exception as monitoring_error:
                self.logger.warning(f"Error monitoring VM {vm.name}: {monitoring_error}")

    def _handle_vm_failure(self, failed_vm):
        """
        Advanced VM failure handling with retry mechanism
        """
        current_retries = self.failed_vm_retries.get(failed_vm.name, 0)
        
        if current_retries < self.max_retries:
            self.logger.warning(
                f"Detected failure in VM: {failed_vm.name}. "
                f"Retry attempt {current_retries + 1}/{self.max_retries}"
            )
            
            try:
                self.fault_tolerance_manager.handle_vm_failure(failed_vm)
                self.failed_vm_retries[failed_vm.name] = current_retries + 1
            except Exception as recovery_error:
                self.logger.error(f"Recovery attempt failed for {failed_vm.name}: {recovery_error}")
        else:
            self.logger.critical(
                f"VM {failed_vm.name} has exceeded maximum recovery attempts. "
                "Manual intervention required."
            )
