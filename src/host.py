from abc import ABCMeta, abstractmethod
from dut_interface import DutInterface
# Observable
class Host(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Host:
            if any("__usb_list__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

    @abstractmethod    
    def __usb_list__(self):
        pass
    
    @abstractmethod
    def get_next_usb_device(self):
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
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass
