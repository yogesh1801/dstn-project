import time
from threading import Thread


class FaultToleranceManager:
    def __init__(self, raid_manager):
        self.raid_manager = raid_manager

    def handle_vm_failure(self, failed_vm):
        """
        Handle VM failure and reconstruct data.

        :param failed_vm: Docker container of failed VM
        """
        print(f"Handling failure for VM: {failed_vm.name}")

        failed_vm.remove(force=True)
        new_vm = self.raid_manager.docker_client.containers.run(
            "ubuntu:latest",
            name="video-storage-vm-recovery",
            volumes={"/data/raid_vm_recovery": {"bind": "/mnt/storage", "mode": "rw"}},
            detach=True,
            command="tail -f /dev/null",
        )
        # surviving_vms = [vm for vm in self.raid_manager.vms if vm.id != failed_vm.id]
        self.raid_manager.sync_data("/mnt/storage", [new_vm])
        self.raid_manager.vms.append(new_vm)
        print(f"Recovered VM: {new_vm.name}")


class FaultToleranceMonitor(Thread):
    def __init__(self, raid_manager, fault_tolerance_manager, interval=10):
        super().__init__(daemon=True)
        self.raid_manager = raid_manager
        self.fault_tolerance_manager = fault_tolerance_manager
        self.interval = interval

    def run(self):
        """Continuously monitor VMs for failures and handle recovery."""
        try:
            while True:
                for vm in self.raid_manager.vms:
                    vm.reload()
                    if vm.status != "running":
                        print(f"Detected failure in VM: {vm.name}")
                        self.fault_tolerance_manager.handle_vm_failure(vm)
                time.sleep(self.interval)
        except Exception as e:
            print(f"Error during VM monitoring: {e}")
        except KeyboardInterrupt:
            print("VM monitoring stopped.")
