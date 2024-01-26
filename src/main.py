#!/usr/bin/env python
import asyncio
from enum import Enum, unique
import logging
import platform
import sys
from host import Host
from windows_host import WindowsHost
from linux_host import LinuxHost
from dut_interface import DutInterface
from sdwire import SDWireC

logger = logging.getLogger(__name__)


@unique
class BadgerdDevice(Enum):
    SDWIREC = 1
    USBMUX = 2
    UNKNOWN = -1


def get_device(dut_type: str):
    # print("dut type: ", f"{dut_type}")
    if dut_type == "1":
        return SDWireC()
    # elif ..
    else:
        return None


if __name__ == "__main__":
    host: Host = None
    dut: DutInterface = None
    badgerd_device: BadgerdDevice = BadgerdDevice.UNKNOWN
    serial_no_input: str = ""
    while badgerd_device == BadgerdDevice.UNKNOWN:
        print(
            "Please choose the device you want to initialize and press Enter:\n",
            "Badgerd SDWireC: 1,\n",
            "Badgerd USB Mux: 2\n",
        )
        dut_type_input: str = input()
        serial_no_input = ""
        if dut_type_input == "1":
            badgerd_device = BadgerdDevice.SDWIREC
            print("Please enter a number to start initilization with it: ")
            serial_no_input = input()
            while int(serial_no_input) <= 0 or int(serial_no_input)>1000:
                print("Please enter a valid number (>1, <=1000)")
                serial_no_input = input()
            break
        elif dut_type_input == "2":
            badgerd_device = BadgerdDevice.USBMUX
            break
        else:
            badgerd_device = BadgerdDevice.UNKNOWN
            print(
                "Device type couldn't recognized. Enter Yes[Y] to continue and choose a valid device, enter No[N] to quit\n"
            )
            answer = ""
            while answer not in [
                "Y",
                "y",
                "Yes",
                "yes",
                "[Y]",
                "[y]",
                "N",
                "n",
                "No",
                "no",
                "[N]",
                "[n]",
            ]:
                answer: str = input()
                if answer in ["Y", "y", "Yes", "yes", "[Y]", "[y]"]:
                    pass
                elif answer in ["N", "n", "No", "no", "[N]", "[n]"]:
                    print("Good Bye!")
                    exit()
                else:
                    print("Press Y for continue or N for exit")
    print(badgerd_device.name)
    if platform.system() == "Windows":
        host: Host = WindowsHost()
        print("Windows")
    elif platform.system() == "Linux":
        host = LinuxHost()
        # dut_type_input enum
        if badgerd_device == BadgerdDevice.SDWIREC:
            dut = SDWireC("Linux", int(serial_no_input))
        host.attach(dut)
        try:
            asyncio.run(host.main())
        except KeyboardInterrupt:
            print("\nSystem is terminating")
    else:
        raise Exception("Unknown Operating System")
