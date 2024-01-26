from abc import ABCMeta, abstractmethod
from dut_interface import DutInterface
import asyncio


# Observable
class Host(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        return (
            hasattr(subclass, "attach")
            and callable(subclass.attach)
            and hasattr(subclass, "main")
            and callable(subclass.main)
            and hasattr(subclass, "detach")
            and callable(subclass.detach)
            and hasattr(subclass, "notify")
            and callable(subclass.notify)
            or NotImplemented
        )

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

    @abstractmethod
    async def main(self):
        pass
