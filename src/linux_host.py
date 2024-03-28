import asyncio
import signal
from typing import List
import time

import janus
from pyudev import Context, Monitor, MonitorObserver, Device

from host import Host
from dut_interface import DutInterface
from sdwire import SDWireC
from peripheral import USBDevice


class LinuxHost(Host):
    def __init__(self):
        self._observers: List[DutInterface] = []
        self._context: Context = Context()
        self._monitor: Monitor = Monitor.from_netlink(context=self._context)
        self._monitor.filter_by(subsystem="usb")

    def attach(self, dut: DutInterface):
        self._observers.append(dut)

    def detach(self, dut: DutInterface):
        self._observers.remove(dut)

    def on_usb_attach(self, device: Device):
        if device.action == "add":
            print(
                f"New USB device is found with ID: {device.properties.get('ID_SERIAL_SHORT')}, partition {device.device_path}"
            )
            self.device_queue.sync_q.put(device)
        elif device.action == "remove":
            print(f"{device} is removed")
        else:
            pass

    async def notify(self):
        await asyncio.sleep(1)
        if (usb_device := await self.device_queue.async_q.get()) != None:
            if usb_device.properties.get("ID_SERIAL_SHORT") != None:
                badgerd_device: USBDevice = USBDevice()
                badgerd_device.serial_no = usb_device.properties.get("ID_SERIAL_SHORT")
                badgerd_device.vendor_id = usb_device.properties.get("ID_VENDOR_ID")
                badgerd_device.product_id = usb_device.properties.get("ID_MODEL_ID")
                for observer in self._observers:
                    await observer.update(device=badgerd_device)

    async def main(self):
        keep_run: bool = True
        loop = asyncio.get_running_loop()
        self.device_queue = janus.Queue()
        self.p_observer = MonitorObserver(
            self._monitor, callback=self.on_usb_attach, name="monitor-observer"
        )
        self.p_observer.start()
        while keep_run:
            try:
                notify = asyncio.create_task(self.notify())
                await notify
            except KeyboardInterrupt:
                print("program will be terminated.")
                keep_run = False
                tasks = asyncio.all_tasks(loop=loop)
                for task in tasks:
                    task.cancel("{task} is cancelling")
                group = asyncio.gather(*tasks, return_exceptions=True)
                loop.run_until_complete(group)
                loop.close()


if __name__ == "__main__":
    l_host = LinuxHost()
    sdwire = SDWireC("Linux", 302)
    l_host.attach(sdwire, "sdwire")
    asyncio.run(l_host.main())
