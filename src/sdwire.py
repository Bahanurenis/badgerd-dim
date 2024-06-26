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
                f"{Fore.MAGENTA}Initialization is starting, please don't remove the device until initilization is done{Style.RESET_ALL}"
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
                        f"{Fore.GREEN}Initialization is done, new serial id will become {Style.RESET_ALL} bdgrd_sdwirec_{self._serial_number}\n",
                    )
                    print(completed_process.stdout)
                    self._serial_number += 1
                    print(f"Next serial id will be {self._serial_number}")
                else:
                    print(completed_process.stderr)
            except subprocess.CalledProcessError as e:
                print(
                    f"{Fore.RED}Initialization command is failed with {Style.RESET_ALL}{e}"
                )
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
                    f"{Fore.GREEN}New Badgerd SDWireC is found: {completed_process.stdout} {Style.RESET_ALL}"
                )

            else:
                print(
                    f"{Fore.RED}Badgerd SDWireC is not found{Style.RESET_ALL} {completed_process.stderr}"
                )

    async def test(self, device: USBDevice):
        if self._os == "Linux":
            print("Tests are starting...")
            partition_path = ""
            await self.ts_test_linux(device=device)
            await asyncio.sleep(2)
            await self.dut_test_linux(device=device)
            print("test is finished, you can remove the device")
            await asyncio.sleep(2)

    async def ts_test_linux(self, device: USBDevice):
        print(
            f"{Fore.BLUE}================ TS mode test ===============\n{Style.RESET_ALL}"
        )
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
            print(
                f"{Fore.YELLOW}Storage couldn't find, --ts mode test will skip...{Style.RESET_ALL}"
            )
        else:
            destination = "/dev/" + partition_path
            if ts_mode_returncode == 0:
                print("Test result of writing 2000 KB:")
                write_task = asyncio.create_task(
                    self.write_data_to_device(destination, "1K", "2000")
                )
                await write_task
                write_test_returncode = write_task.result()
                if write_test_returncode == 0:
                    print(
                            f"{Fore.GREEN}Data has been written successfully. Reading test will start...{Style.RESET_ALL}"
                        )
                    read_task = asyncio.create_task(
                        self.read_data_from_device(destination)
                    )
                    await read_task
                await asyncio.sleep(1)
                print("Test result of writing 100 MB data: ")
                write_task_2 = asyncio.create_task(
                    self.write_data_to_device(destination, "50M", "2")
                )
                await write_task_2
                write_test_2_returncode = write_task_2.result()
                if write_test_2_returncode == 0:
                    print(
                            f"{Fore.GREEN}Data has been written successfully. Reading test will start...{Style.RESET_ALL}"
                        )
                    read_task_2 = asyncio.create_task(
                        self.read_data_from_device(destination)
                    )
                    await read_task_2
            await asyncio.sleep(1)
            print("--ts test is finished")

    async def dut_test_linux(self, device: USBDevice):
        print(
            f"{Fore.CYAN}================ DUT mode test ===============\n{Style.RESET_ALL}"
        )
        ts_mode_task = asyncio.create_task(
            self.change_device_mode(device.serial_no, "ts")
        )
        await ts_mode_task
        dut_mode_task = asyncio.create_task(
            self.change_device_mode(device.serial_no, "dut")
        )
        await dut_mode_task
        dut_mode_returncode = dut_mode_task.result()
        answer = ""
        print(
            f"{Fore.BLUE}Make sure BLUE LED is turned on on the SDWireC.{Style.RESET_ALL}"
        )
        print(
            "Please place the SDWire SD Card reader slot and connect with DUT device..."
        )
        answer = input("If you are done, please press a key and Enter to continue: ")
        if answer != "":
            answer = ""
            find_partition_task = asyncio.create_task(self.find_sdcard_partition())
            await find_partition_task
            partition_path: str = find_partition_task.result()
            await asyncio.sleep(1)
            if partition_path == "":
                print(
                    f"{Fore.YELLOW}Storage couldn't find, --dut mode test will skip...{Style.RESET_ALL}"
                )
            else:
                destination = "/dev/" + partition_path
                if dut_mode_returncode == 0:
                    print("Test result of writing 2000 KB:")
                    write_task = asyncio.create_task(
                        self.write_data_to_device(destination, "1K", "2000")
                    )
                    await write_task
                    write_test_returncode = write_task.result()
                    if write_test_returncode == 0:
                        print(
                            f"{Fore.GREEN}Data has been written successfully. Reading test will start...{Style.RESET_ALL}"
                        )
                        read_task = asyncio.create_task(
                            self.read_data_from_device(destination)
                        )
                        await read_task
                    await asyncio.sleep(1)
                    print("Test result of writing 100MB data: ")
                    write_task_2 = asyncio.create_task(
                        self.write_data_to_device(destination, "50M", "2")
                    )
                    await write_task_2
                    write_test_2_returncode = write_task_2.result()
                    if write_test_2_returncode == 0:
                        print(
                            f"{Fore.GREEN}Data has been written successfully. Reading test will start...{Style.RESET_ALL}"
                        )
                        read_task_2 = asyncio.create_task(
                            self.read_data_from_device(destination)
                        )
                        await read_task_2
                await asyncio.sleep(1)
        print("--dut test is finished")
        pass

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
            elif "detected capacity change from 0 to" in line:
                l_line = line.split()
                break

        for item in l_line:
            if "[sd" in item:
                partition_path = item.strip("[]")
                print(f"partition path: {partition_path}")
                break
            elif "sd" in item:
                partition_path = item.strip(":")
                print(f"partition path: {partition_path}")
        return partition_path

    async def write_data_to_device(self, destination: str, data_size: str, count: str):
        write_dd_cmd = [
            "dd",
            "if=/dev/zero",
            f"of={destination}",
            f"bs={data_size}",
            f"count={count}",
        ]
        write_test_subprocess = subprocess.run(
            f'sudo {" ".join(write_dd_cmd)}',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
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
    write_cmd = [
        "dd",
        "if=/dev/zero",
        "of=/home/talha/workspace/badgerd-dim/dd_input.txt",
        f"bs=1K",
        f"count=1",
        "oflag=direct",
        "status=progress",
    ]
    write_test_subprocess = subprocess.run(
        f'sudo {" ".join(write_cmd)}',
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
    )
    print(write_test_subprocess.stdout)
