import logging
import platform
from host import Host
from windows_host import WindowsHost
from linux_host import LinuxHost
from dut_interface import DutInterface
from sdwire import SDWireC

logger = logging.getLogger(__name__)
def get_device(dut_type:str):
    # print("dut type: ", f"{dut_type}")
    if dut_type == "1":
        return SDWireC()
    # elif .. 
    else: 
        return None


if __name__ == "__main__":
    host: Host = None
    #TODO: Make dut None in the below in product code
    dut:DutInterface = SDWireC()

    # TODO: Activate below in product
    # print("Please choose the device you want to initialize and press Enter:\n",
    # "Badgerd SDWireC: 1,\n", "Badgerd USB Mux: 2\n")
    # dut_type_input: str = input()
    # dut = get_device(dut_type_input)
    # while dut == None:
    #     print("Device type couldn't recognized. Enter Yes[Y] to continue and choose a valid device, enter No[N] to quit\n")
    #     answer: str = input()
    #     if answer in ["Y","y", "Yes", "yes", "[Y]", "[y]"]:
    #         print("Please choose the device you want to initialize and press Enter:\n",
    #         "Badgerd SDWireC: 1,\n", 
    #         "Badgerd USB Mux: 2\n")
    #         dut_type_input = input()
    #         dut = get_device(dut_type_input)
    #     elif answer in ["N","n", "No", "no", "[N]", "[n]"]:
    #         print("Good Bye!")
    #         exit() 

    if platform.system() == "Windows":
        host: Host = WindowsHost()
        print("Windows")
    elif platform.system() == "Linux":
        host = LinuxHost()
        print("Linux")
    else: 
        raise Exception("Unknown Operating System")
 
    # for device in host.get_next_usb_device():
    #     pass
        # dut.initialize(device.vendor_id

    pass
