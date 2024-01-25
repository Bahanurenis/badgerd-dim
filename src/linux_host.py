from host import Host
import subprocess
from typing import List
from dut_interface import DutInterface


class LinuxHost(Host):
    _observes: List[DutInterface] = []

    def __init__(self):
        pass

    def attach(self, dut: DutInterface):
        self._observers.append(dut)

    def detach(self, dut: DutInterface):
        if dut in _observers:
            self._observers.remove(dut)

    async def notify(self, usb_device):
        print("inside the notify function")
        for observer in self._observers:
            # we definitely should wait the observer update returns.
            await observer.update(usb_device)

    async def listen_usb_events(self):
        pass
