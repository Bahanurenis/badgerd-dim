
from __future__ import annotations
import abc

class DutInterface(metaclass=abc.ABCMeta):
    """ A meta class for USB devices """
        # def __instancecheck__(cls, instance):
        #     return cls.__subclasscheck__(type(instance))
    @classmethod
    def __subclasshook__(cls, subclass):
        print('test')
        return (hasattr(subclass, 'initialize') and 
            callable(subclass.initialize) and 
            hasattr(subclass, 'validate') and 
            callable(subclass.validate) and 
            hasattr(subclass, 'test') and 
            callable(subclass.test) or 
            NotImplemented)
            
    def initialize(self):
        pass
    def validate(self):
        pass
    @abc.abstractmethod
    def test(self):
        pass 
    
    # we will call initiliaze or test in here  
    @abc.abstractmethod
    def update(self, n_device) -> None:
        """
        Receive update from host.
        """
        pass
