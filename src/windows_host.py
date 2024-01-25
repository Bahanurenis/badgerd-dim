from host import Host
import subprocess, json
from typing import List

from dut_interface import DutInterface


class WindowsHost(Host):
    usb_dict: dict = {}
    _observers: List[DutInterface] = []

    def __init__(self):
        self.__usb_list__()

    def attach(self, observer: DutInterface) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: DutInterface) -> None:
        self._observers.remove(observer)

    #  we will call this function if usb device is connected with system
    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """

        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)

    def __usb_list__(self):
        #  Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Format-List
        print("Hello")
        out = subprocess.getoutput(
            "PowerShell -Command \"& {Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Select-Object Status,Class,FriendlyName,InstanceId,Manufacturer | ConvertTo-Json}\""
        )
        j = json.loads(out)
        for dev in j:
            # print(dev, type(dev["InstanceId"]))
            # print( "Instance Id: " + dev['InstanceId'], "Manufacturer Id: " + dev['Manufacturer'])
            self._get_device_descriptor(dev["InstanceId"])

    def _get_device_descriptor(self, device_instance_id: str):
        instance: list = device_instance_id.split("\\")
        # product: list = instance[1].split("&")
        print(instance)

    def get_next_usb_device(self):
        # send the new device as a parameter
        self.notify()
        pass
