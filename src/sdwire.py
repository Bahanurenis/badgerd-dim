from dut_interface import DutInterface


class SDWireC(DutInterface):
    def __init__(self):
        self._device_number = "-1"
        self._vendor = ""
        self._product = ""
        self._serial_no = ""

    def initialize(
        self,
        device_number,
        vendor_id,
    ):
        pass

    def validate(self):
        pass

    def test(self):
        pass

    def update(self):
        pass
