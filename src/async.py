import win32api, win32con, win32gui
from ctypes import *
import wmi
import asyncio
import sys, os
from typing import List
import signal
import functools
from multiprocessing import Process
import aiomultiprocess
from pynput import keyboard
import time

""" This class aim to test asyncio feature for the system."""


class SdWireTest:
    """
    This class mimics the SDWireC class
    """

    async def update(self, device):
        # This function should be uncancelled.
        print("observer update function\n")
        print(device)


class WindowsTest:
    """
    This class mimics the WindowsHost class
    """

    _observers: List[SdWireTest] = []
    backgroud_tasks = set()
    key_pressed = {"pressed": False, "released": False}

    def attach(self, dut: SdWireTest):
        self._observers.append(dut)

    def detach(self, dut: SdWireTest):
        if dut in _observers:
            self._observers.remove(dut)

    async def notify(self, usb_device):
        print("inside the notify function")
        for observer in self._observers:
            # we definitely should wait the observer update returns.
            await observer.update(usb_device)

    async def on_usb_connect(self):
        # This is a event that will fire when a new usb device connected with Windows machine
        raw_wql = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBHub'"
        c = wmi.WMI()
        # watcher = c.watch_for(raw_wql=raw_wql, notification_type="Creation" , wmi_class="Win32_USBHub", delay_secs=1)
        watcher = c.watch_for(raw_wql=raw_wql)
        # await asyncio.sleep(1)
        print("on_usb_connect is called")
        # every watcher() will call next
        return watcher()

    def on_key_press(self, key):
        # flag = "pressed"
        if key == keyboard.Key.esc:
            print("esc is pressed")
            self.key_pressed["pressed"] = True

    def on_key_release(self, key: keyboard.Key):
        flag = "released"
        if key == keyboard.Key.esc:
            print("esc is released")
            self.key_pressed["released"] = True

    async def listen_keypress_events(self):
        loop = asyncio.get_event_loop()
        listener = keyboard.Listener(
            on_press=self.on_key_press, on_release=self.on_key_release
        )
        listener.start()
        # await loop.run_in_executor(None, time.sleep,2)
        while True:
            print("Press ESC if you want to exit to app")
            await loop.run_in_executor(None, time.sleep, 1)
            if (
                self.key_pressed["pressed"] == True
                or self.key_pressed["released"] == True
            ):
                print("listen key press will be return True")
                self.key_pressed["released"] = False
                self.key_pressed["pressed"] = False
                listener.stop()
                await self.shutdown(loop)
                return True
            else:
                await self.listen_usb_events()

    async def listen_usb_events(self):
        print("Start listen usb events")
        usb_detect_task = asyncio.create_task(self.on_usb_connect())
        await usb_detect_task
        device = usb_detect_task.result()
        notify_task = asyncio.create_task(self.notify(device))
        await notify_task
        # device = usb_detect_task.result()
        # TODO: wait_for/ wait can be used?
        self.backgroud_tasks.add(usb_detect_task)
        self.backgroud_tasks.add(notify_task)

        # print("device: ", device)
        print("inside listener")
        usb_detect_task.add_done_callback(self.backgroud_tasks.discard)
        notify_task.add_done_callback(self.backgroud_tasks.discard)

    async def shutdown(self, loop):
        print("Shutdown process is beginning ")
        tasks = []
        for task in asyncio.all_tasks(loop):
            if task != None:
                if task != asyncio.current_task():
                    task.cancel()
                    tasks.append(task)
                else:
                    loop.run_until_complete(task)
                    tasks.remove(task)

    async def main(self):
        loop = asyncio.get_event_loop()
        task_shutdown = asyncio.create_task(self.listen_keypress_events())
        await task_shutdown
        result = task_shutdown.result()
        if result == True:
            loop.stop()
            loop.close
            return False


# TODO: Will Gracefully exit parallel too

if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    print("Hello Moto")
    w = WindowsTest()
    sdwire = SdWireTest()
    w.attach(sdwire)
    with asyncio.runners.Runner() as runner:
        try:
            runner.run(w.main())
        except RuntimeError:
            print("ESC is pressed")
        finally:
            print("exit")
            runner.close()
