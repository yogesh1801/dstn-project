import time
import logging
import os
from threading import Thread, Lock
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

class FaultToleranceManager:
    def __init__(self, raid_manager):
        self.raid_manager = raid_manager
        self.logger = logging.getLogger(__name__)
        self.recovery_lock = Lock()
        self.last_sync_time = {}
        self.primary_vm_health = True

    def handle_vm_failure(self, failed_vm, is_primary=False):
        """
        Handle VM failure and reconstruct data with improved error handling
        and primary VM failover support.

        :param failed_vm: Docker container of failed VM
        :param is_primary: Boolean indicating if failed VM is primary
        """
        with self.recovery_lock:
            self.logger.info(f"Handling failure for VM: {failed_vm.name} (Primary: {is_primary})")
            
            try:
                # Store failed VM's index for proper replacement
                failed_vm_index = self.raid_manager.vms.index(failed_vm)
                
                # Remove failed VM
                failed_vm.remove(force=True)
                self.logger.debug(f"Removed failed VM: {failed_vm.name}")

                # Create recovery VM
                vm_data_path = os.path.join(os.getcwd(), f"storage/raid_vm_{failed_vm_index}")
                os.makedirs(vm_data_path, exist_ok=True)
                
                new_vm = self.raid_manager.docker_client.containers.run(
                    "ubuntu:latest",
                    name=f"video-storage-vm-{failed_vm_index}",
                    volumes={
                        vm_data_path: {"bind": "/mnt/storage", "mode": "rw"}
                    },
                    detach=True,
                    command="tail -f /dev/null",
                    restart_policy={"Name": "unless-stopped"}
                )
                
                self.logger.info(f"Created new recovery VM: {new_vm.name}")

                # Handle primary VM failure
                if is_primary:
                    self._handle_primary_failure(new_vm, failed_vm_index)
                else:
                    self._handle_secondary_failure(new_vm)

                # Update VM list
                self.raid_manager.vms[failed_vm_index] = new_vm
                self.last_sync_time[new_vm.name] = datetime.now()
                
                self.logger.info(f"Successfully recovered VM: {new_vm.name}")
                return new_vm

            except Exception as e:
                self.logger.error(f"Critical error during VM recovery: {e}")
                self.primary_vm_health = False
                raise

    def _handle_primary_failure(self, new_vm, failed_vm_index):
        """
        Handle primary VM failure with failover
        """
        self.logger.info("Initiating primary VM failover process")
        
        try:
            # Select most up-to-date secondary VM as data source
            source_vm = self._select_best_secondary()
            if not source_vm:
                raise Exception("No healthy secondary VMs available for failover")

            # Sync data from selected secondary to new primary
            self.raid_manager.sync_data("/mnt/storage", [new_vm], source_vm)
            
            # Update primary VM index
            self.raid_manager.primary_vm_index = failed_vm_index
            self.primary_vm_health = True
            
            self.logger.info(f"Primary VM failover completed. New primary: {new_vm.name}")

        except Exception as e:
            self.logger.error(f"Primary VM failover failed: {e}")
            raise

    def _handle_secondary_failure(self, new_vm):
        """
        Handle secondary VM failure and data reconstruction
        """
        try:
            primary_vm = self.raid_manager.vms[self.raid_manager.primary_vm_index]
            self.raid_manager.sync_data("/mnt/storage", [new_vm], primary_vm)
            self.logger.info(f"Secondary VM recovery completed: {new_vm.name}")
        
        except Exception as e:
            self.logger.error(f"Secondary VM recovery failed: {e}")
            raise

    def _select_best_secondary(self):
        """
        Select the most up-to-date secondary VM for failover
        """
        secondary_vms = [vm for i, vm in enumerate(self.raid_manager.vms) 
                        if i != self.raid_manager.primary_vm_index]
        
        if not secondary_vms:
            return None

        # Select VM with most recent sync
        return max(secondary_vms, 
                  key=lambda vm: self.last_sync_time.get(vm.name, datetime.min))


class FaultToleranceMonitor(Thread):
    def __init__(self, raid_manager, fault_tolerance_manager, 
                 interval=10, max_retries=3, health_check_timeout=5):
        super().__init__(daemon=True)
        self.raid_manager = raid_manager
        self.fault_tolerance_manager = fault_tolerance_manager
        self.interval = interval
        self.max_retries = max_retries
        self.health_check_timeout = health_check_timeout
        self.logger = logging.getLogger(__name__)
        self.failed_vm_retries = {}
        self.running = True

    def run(self):
        """
        Enhanced VM monitoring with health checks and graceful shutdown
        """
        self.logger.info("Advanced fault tolerance monitoring started")
        
        while self.running:
            try:
                self._monitor_vms()
                time.sleep(self.interval)
            
            except Exception as e:
                self.logger.error(f"Critical monitoring error: {e}")
                time.sleep(self.interval)

    def stop(self):
        """
        Graceful shutdown of monitoring
        """
        self.running = False
        self.join()
        self.logger.info("Fault tolerance monitoring stopped")

    def _monitor_vms(self):
        """
        Comprehensive VM monitoring with advanced health checks
        """
        for i, vm in enumerate(self.raid_manager.vms):
            is_primary = (i == self.raid_manager.primary_vm_index)
            
            try:
                vm.reload()
                health_status = self._check_vm_health(vm)
                
                if not health_status or vm.status != "running":
                    self._handle_vm_failure(vm, is_primary)
                else:
                    # Reset retry counter on successful health check
                    if vm.name in self.failed_vm_retries:
                        del self.failed_vm_retries[vm.name]

            except Exception as e:
                self.logger.warning(f"Error monitoring VM {vm.name}: {e}")

    def _check_vm_health(self, vm):
        """
        Perform detailed health check on VM
        """
        try:
            # Check basic container health
            vm.reload()
            if vm.status != "running":
                return False

            # Check disk space
            df_result = vm.exec_run("df -h /mnt/storage")
            if df_result.exit_code != 0:
                self.logger.warning(f"Disk space check failed for {vm.name}")
                return False

            # Check process health
            ps_result = vm.exec_run("ps aux")
            if ps_result.exit_code != 0:
                self.logger.warning(f"Process check failed for {vm.name}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Health check failed for {vm.name}: {e}")
            return False

    def _handle_vm_failure(self, failed_vm, is_primary):
        """
        Enhanced VM failure handling with retry mechanism and primary failover
        """
        current_retries = self.failed_vm_retries.get(failed_vm.name, 0)
        
        if current_retries < self.max_retries:
            self.logger.warning(
                f"Detected failure in VM: {failed_vm.name} "
                f"(Primary: {is_primary}). "
                f"Retry attempt {current_retries + 1}/{self.max_retries}"
            )
            
            try:
                self.fault_tolerance_manager.handle_vm_failure(failed_vm, is_primary)
                self.failed_vm_retries[failed_vm.name] = current_retries + 1
            
            except Exception as e:
                self.logger.error(f"Recovery attempt failed for {failed_vm.name}: {e}")
                
                if is_primary:
                    self._initiate_emergency_failover()
        
        else:
            self.logger.critical(
                f"VM {failed_vm.name} has exceeded maximum recovery attempts. "
                "Manual intervention required."
            )

    def _initiate_emergency_failover(self):
        """
        Emergency failover procedure when primary recovery fails
        """
        self.logger.critical("Initiating emergency failover procedure")
        
        try:
            # Find healthy secondary VM
            secondary_vms = [vm for i, vm in enumerate(self.raid_manager.vms) 
                           if i != self.raid_manager.primary_vm_index and 
                           self._check_vm_health(vm)]
            
            if not secondary_vms:
                raise Exception("No healthy secondary VMs available for emergency failover")

            # Select new primary
            new_primary = secondary_vms[0]
            new_primary_index = self.raid_manager.vms.index(new_primary)
            
            # Update primary index
            self.raid_manager.primary_vm_index = new_primary_index
            self.logger.info(f"Emergency failover completed. New primary: {new_primary.name}")
        
        except Exception as e:
            self.logger.critical(f"Emergency failover failed: {e}")
            raise