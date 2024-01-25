from abc import ABCMeta, abstractmethod
from dut_interface import DutInterface
import asyncio


# Observable
class Host(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        return (
            hasattr(subclass, "get_device")
            and callable(subclass.get_device)
            and hasattr(subclass, "attach")
            and callable(subclass.attach)
            and hasattr(subclass, "detach")
            and callable(subclass.detach)
            and hasattr(subclass, "notify")
            and callable(subclass.notify)
            or NotImplemented
        )

    @abstractmethod
    async def get_device(self):
        pass

    @abstractmethod
    def attach(self, observer: DutInterface) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: DutInterface) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    async def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass
