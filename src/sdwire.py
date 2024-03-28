import asyncio
import logging
import re
import subprocess
from colorama import init, Fore, Back, Style
from dut_interface import DutInterface
from peripheral import USBDevice


class SDWireC(DutInterface):
    def __init__(self, _os: str, serial_no: int):
        self._serial_number = serial_no
        self._os = _os

    async def initialize(self, device: USBDevice):
        if self._os == "Linux":
            # call linux_initialize subprocess
            print(
                Fore.BLUE,
                "Initialization is starting, please don't remove the device until initilization is done",
            )
            initialization_cmd = [
                "sd-mux-ctrl",
                f"--device-serial={device.serial_no}",
                f"--vendor=0x{device.vendor_id}",
                f"--product=0x{device.product_id}",
                "--device-type=sd-wire",
                f"--set-serial=bdgrd_sdwirec_{self._serial_number}",
            ]
            try:
                completed_process = subprocess.run(
                    f'sudo {" ".join(initialization_cmd)}',
                    text=True,
                    capture_output=True,
                    shell=True,
                )
                if completed_process.returncode == 0:
                    print(
                        Fore.GREEN,
                        f"Initialization is done, new serial id will become bdgrd_sdwirec_{self._serial_number}\n",
                    )
                    print(completed_process.stdout)
                    self._serial_number += 1
                    print(f"Next serial id will be {self._serial_number}")
                else:
                    print(completed_process.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Initialization command is failed with {e}")
        elif self._os == "Windows":
            #  call windows sub process
            pass

    async def validate(self, device: USBDevice):
        if self._os == "Linux":
            list_sdwire_cmd = ["sd-mux-ctrl", f"--list"]
            completed_process = subprocess.run(
                f'sudo {" ".join(list_sdwire_cmd)}',
                text=True,
                capture_output=True,
                shell=True,
            )
            if (
                completed_process.returncode == 0
                and device.serial_no in completed_process.stdout
            ):
                print(
                    Fore.GREEN,
                    "New Badgerd SDWireC is found:",
                    completed_process.stdout,
                )

            else:
                print(
                    Fore.RED, "Badgerd SDWireC is not found", completed_process.stderr
                )
        print(Fore.RESET, "")

    async def test(self, device: USBDevice):
        if self._os == "Linux":
            print(Fore.BLUE, "Tests are starting...")
            partition_path = ""
            await self.ts_test_linux(device=device)
            await asyncio.sleep(2)
            # await self.dut_test_linux(device=device)
            print(Fore.RESET, "test is finished, you can remove the device")
            await asyncio.sleep(2)

    async def change_device_mode(self, device_serial_no: str, mode: str) -> int:
        _cmd = ["sd-mux-ctrl", f"--device-serial={device_serial_no}", f"--{mode}"]
        sdwire_mode_change_subprocess = subprocess.run(
            f'sudo {" ".join(_cmd)}',
            text=True,
            capture_output=True,
            shell=True,
        )
        await asyncio.sleep(1)
        return sdwire_mode_change_subprocess.returncode

    async def find_sdcard_partition(self):
        print("SD card is checking...\n")
        dmesg_h_read_cmd = ["dmesg", "--time-format=ctime"]
        l_line: list = []
        partition_path: str = ""
        dmesg_sub_process = subprocess.run(
            f'sudo {" ".join(dmesg_h_read_cmd)}',
            capture_output=True,
            text=True,
            shell=True,
        )
        for line in dmesg_sub_process.stdout.splitlines()[::-1]:
            if "Attached SCSI removable disk" in line:
                l_line = line.split()
                break
        for item in l_line:
            if "[sd" in item:
                partition_path = item.strip("[]")
                print(f"partition path: {partition_path}")
                break
        return partition_path

    async def write_data_to_device(self, destination: str, data_size: str, count: str):
        write_dd_cmd = [
            "dd",
            "if=/dev/zero",
            f"of={destination}",
            f"bs={data_size}",
            f"count={count}"
        ]
        write_test_subprocess = subprocess.run(
            f'sudo {" ".join(write_dd_cmd)}',
            capture_output=True,
           text=True,
            shell=True,
        )
        await asyncio.sleep(2)
        print(f"test result: {write_test_subprocess.stdout}")
        return write_test_subprocess.returncode

    async def read_data_from_device(self, destination: str):
        read_hdparm_cmd = ["hdparm", "-Tt", f"{destination}"]
        read_test_subprocess = subprocess.run(
            f'sudo {" ".join(read_hdparm_cmd)}',
            capture_output=True,
            universal_newlines=True,
            shell=True,
        )
        await asyncio.sleep(1)
        print(f"read performance result: {read_test_subprocess.stdout}")

    async def ts_test_linux(self, device: USBDevice):
        print("================ TS mode test ===============\n")
        dut_mode_task = asyncio.create_task(
            self.change_device_mode(device.serial_no, "dut")
        )
        await dut_mode_task
        ts_mode_task = asyncio.create_task(
            self.change_device_mode(device.serial_no, "ts")
        )
        await ts_mode_task
        ts_mode_returncode = ts_mode_task.result()
        await asyncio.sleep(1)
        find_partition_task = asyncio.create_task(self.find_sdcard_partition())
        await find_partition_task
        partition_path: str = find_partition_task.result()
        await asyncio.sleep(1)
        if partition_path == "":
            print("Storage couldn't find, --ts mode test will skip...")
        else:
            destination = "/dev/" + partition_path
            if ts_mode_returncode == 0:
                print("Test result of writing 2000 KB:")
                write_task = asyncio.create_task(
                    self.write_data_to_device(destination, "1K", "2000")
                )
                await write_task
                write_2KkB_test_returncode = write_task.result()
                if write_2KkB_test_returncode == 0:
                    print(
                        "Data has been written successfully. Reading test will start..."
                    )
                    read_task = asyncio.create_task(
                        self.read_data_from_device(destination)
                    )
                    await read_task
                await asyncio.sleep(1)
                # print("Test result of writing 1GB data: ")
                # write_1GB_test_returncode = self.write_data_to_device(
                #     destination, "1GB", "1"
                # )
                # if rite_1GB_test_returncode == 0:
                #     self.read_data_from_device(destination)
            await asyncio.sleep(1)
            print("--ts test is finished")

    async def update(self, device: USBDevice):
        if (
            device.vendor_id == "0403"
            and device.serial_no.startswith("bdgrd_sdwirec") == False
        ):
            initialize_task = asyncio.create_task(self.initialize(device=device))
            await initialize_task
        elif device.serial_no.startswith("bdgrd_sdwirec") == True:
            print("Validating SDWireC.")
            sdwirec_validate = asyncio.create_task(self.validate(device=device))
            await sdwirec_validate
            sdwire_test = asyncio.create_task(self.test(device=device))
            await sdwire_test
        # storage:


if __name__ == "__main__":
    sdwire_test = SDWireC("Linux", 100)
    # sdwire_test.test()
    logging.info("Hello Moto")
    asyncio.run(sdwire_test.ts_test_linux())
    pass
