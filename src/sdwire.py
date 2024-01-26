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
                Fore.BLUE, "Initialization is starting, please don't remove the device until initilization is done"
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
                    print(Fore.GREEN,
                     f"Initialization is done, new serial id will become bdgrd_sdwirec_{self._serial_number}\n"
                    )
                    print(completed_process.stdout)
                    self._serial_number += 1
                    print(self._serial_number)
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
                print(Fore.GREEN, "New Badgerd SDWireC is found:", completed_process.stdout)
            else:
                print(Fore.RED, "Badgerd SDWireC is not found", completed_process.stderr)

    async def test(self, device: USBDevice):
        if self._os == "Linux":
            print(Fore.BLUE, "Tests are starting...")
            partition_path = ""
            await self.ts_test_linux(
                device=device
                )
            await asyncio.sleep(2)
            await self.dut_test_linux(
                        device=device
                    )
            print(Fore.RESET, "test is finished, you can remove the device")
            await asyncio.sleep(2)

    async def ts_test_linux(self, device: USBDevice):
        print(Fore.MAGENTA, "================ TS mode test ===============\n")
        ts_sdwire_cmd = ["sd-mux-ctrl", f"--device-serial={device.serial_no}", "--ts"]
        dut_sdwire_cmd = ["sd-mux-ctrl", f"--device-serial={device.serial_no}", "--dut"]
        dmesg_h_read_cmd = ["dmesg", "--time-format=ctime"]
         # Pass the dut mode
        dut_sdwire_process = subprocess.run(
            f'sudo {" ".join(dut_sdwire_cmd)}',
            text=True,
            capture_output=True,
            shell=True,
        )
        await asyncio.sleep(1)

        ts_sdwire_process = subprocess.run(
        f'sudo {" ".join(ts_sdwire_cmd)}',
        text=True,
        capture_output=True,
        shell=True,)
        await asyncio.sleep(2)
        print("SD storage is checking...\n")
        l_line:list = []
        partition_path:str = ""
        dmesg_sub_process = subprocess.run( f'sudo {" ".join(dmesg_h_read_cmd)}',capture_output=True, text=True, shell=True)
        await asyncio.sleep(1)
        for line in dmesg_sub_process.stdout.splitlines()[::-1]:
           if "Attached SCSI removable disk" in line:
            l_line = line.split()
            break
        for item in l_line:
            if "[sd" in item:
                partition_path = item.strip("[]")
                print(f"partition path: {partition_path}")
                break
        if partition_path == "": 
             print("Storage couldn't find, --ts mode test will be skipped")
        else:
            destination = "/dev/" + partition_path + "1"
            if ts_sdwire_process.returncode == 0:
                write_2KkB_cmd = ["dd", "if=/dev/zero", f"of={destination}", "bs=1K", "count=2000", "oflag=direct", "status=progress"]
                write_1GB_cmd = ["dd", "if=/dev/zero", f"of={destination}", "bs=1G", "count=1", "oflag=direct", "status=progress"]
                read_cmd = ["hdparm", "-Tt", f"{destination}"]
                print("Test result of writing 2000 KB:")
                write_2KkB_test_subprocess = subprocess.run(
                    f'sudo {" ".join(write_2KkB_cmd)}', capture_output=True,universal_newlines=True, shell=True
                )
                if write_2KkB_test_subprocess.returncode == 0:
                    print(write_2KkB_test_subprocess.stdout)
                    # Read the data 
                    read_2KkB_test_subprocess = subprocess.run(
                    f'sudo {" ".join(read_cmd)}', capture_output=True,text=True, shell=True)
                    if read_2KkB_test_subprocess.returncode == 0:
                        print("Test result of reading  2000 KB:")
                        print(read_2KkB_test_subprocess.stdout)
                await asyncio.sleep(1)
                print("Test result of writing 1GB data: ")
                write_1GB_test_subprocess = subprocess.run(
                    f'sudo {" ".join(write_1GB_cmd)}', capture_output=True,text=True, shell=True
                )
                if write_1GB_test_subprocess.returncode == 0:
                    print(write_1GB_test_subprocess.stdout)
                    # Read data
                    read_1GB_test_subprocess = subprocess.run(
                    f'sudo {" ".join(read_cmd)}', capture_output=True,text=True, shell=True)
                    if read_1GB_test_subprocess.returncode == 0:
                        print("Test result of reading  1GB:")
                        print(read_1GB_test_subprocess.stdout)
            await asyncio.sleep(1)
            print("--ts test is finished")
    
    async def dut_test_linux(self,device:USBDevice):
        print(Fore.YELLOW, "================ DUT mode test ===============\n")
        # ts_sdwire_cmd = ["sd-mux-ctrl", f"--device-serial={device.serial_no}", "--ts"]
        # dut_sdwire_cmd = ["sd-mux-ctrl", f"--device-serial={device.serial_no}", "--dut"]
        # dmesg_h_read_cmd = ["dmesg", "--time-format=ctime"]
        # answer:str = ""
        #  # Pass the ts mode
        # ts_sdwire_process = subprocess.run(
        #     f'sudo {" ".join(ts_sdwire_cmd)}',
        #     text=True,
        #     capture_output=True,
        #     shell=True,
        # )
        # await asyncio.sleep(1)

        # dut_sdwire_process = subprocess.run(
        # f'sudo {" ".join(dut_sdwire_cmd)}',
        # text=True,
        # capture_output=True,
        # shell=True,)
        # await asyncio.sleep(2)
        # print(Fore.BLUE, "Please check blue led is activated on Badgerd SDWireC****")
        # print(Fore.YELLOW, "Placed the SDWireC to SD card reader")
        # print("Attached the SDCard reader to the device...")
        # await asyncio.sleep(1)
        # answer = input("Please press 'y' when you are done: ")
        # if answer == 'y' or answer == 'Y':
        #     print("SD storage is checking...\n")
        #     await asyncio.sleep(1)
        #     l_line:list = []
        #     partition_path:str = ""
        #     dmesg_sub_process = subprocess.run( f'sudo {" ".join(dmesg_h_read_cmd)}',capture_output=True, text=True, shell=True)
        #     await asyncio.sleep(1) 
        
        #     for line in dmesg_sub_process.stdout.splitlines()[::-1]:
        #         if "detected capacity change from 0 to" in line:
        #             l_line = line.split()
        #             break
        #     for item in l_line:
        #         print(item, end=" ")
        #         if "sd" in item:
        #             partition_path = item.strip(":")
        #             print(partition_path)

        #     if partition_path == "": 
        #         print("storage couldn't find, test will be skipped")
        #     else:
        #         mounth_path = "/dev/" + partition_path + "1"
        #         mount_cmd = ["mount", f"{mounth_path}", "/media/test"]
        #         umount_cmd = ["umount", "/media/test"]
        #         print(f"/media/test will be mount with {mounth_path}")
        #         mount_process = subprocess.run(
        #             f'sudo {" ".join(mount_cmd)}', shell=True, text=True, capture_output=True
        #         )
        #         if mount_process.returncode != 0:
        #             print("Unmount process is starting")
        #             umount_process = subprocess.run(f'sudo {" ".join(umount_cmd)}', shell=True,text=True,capture_output=True)
        #             mount_process = subprocess.run(
        #                 f'sudo {" ".join(mount_cmd)}',
        #                 shell=True,
        #                 text=True,
        #                 capture_output=True,
        #             )
            
        #         if dut_sdwire_process.returncode == 0:
        #             create_test_process = subprocess.run(
        #                 f"sudo touch /media/test/sdwiretest", shell=True
        #             )
        #             if create_test_process.returncode == 0:
        #                 print("sudo touch /media/test/sdwiretest")
        #                 print("...................................\n")
        #                 check_test_process = subprocess.run(
        #                     "ls /media/test", shell=True, text=True, capture_output=True
        #                 )
        #                 print("ls /media/test\n", check_test_process.stdout)
        #                 if check_test_process.returncode == 0 and "sdwiretest" in check_test_process.stdout.split("\n"):
        #                     print("test file was created successfully in ts mode")
        #                     print("sudo rm /media/test/sdwiretest\n sdwiretest file will be removed..")
        #                     remove_test_process = subprocess.run(
        #                         f"sudo rm /media/test/sdwiretest",
        #                         shell=True,
        #                         text=True,
        #                         capture_output=True,
        #                     )
        #                 check_remove_process = subprocess.run(
        #                     "ls /media/test", shell=True, text=True, capture_output=True
        #                 )
        #                 print("ls /media/test\n ", check_remove_process.stdout)
        #                 if (
        #                     remove_test_process.returncode == 0
        #                     and "sdwiretest" not in check_remove_process.stdout.split("\n")
        #                 ):
        #                     print("test file removed successfully")
        #         umount_process = subprocess.run(f'sudo {" ".join(umount_cmd)}', shell=True)
        #     await asyncio.sleep(1)
        #     print("DUT test is finished")   
    

    async def update(self, device: USBDevice):
        if device.serial_no == "0403" and device.serial_no.startswith("bdgrd_sdwirec") == False:
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
    asyncio.run(sdwire_test.test())
    pass
