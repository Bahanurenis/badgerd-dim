
class USBDevice:
    def __init__(self):
        self._vendor_id = ""
        self._manufacturer = ""
        self._serial_number = ""
        self._product_id = ""

    @property
    def vendor_id(self):
        return self._vendor_id

    @property
    def product_id(self):
        return self._product_id

    @property
    def manufacturer(self):
        return self._manufacturer

    @property
    def serial_no(self):
        return self._serial_number

    @vendor_id.setter
    def vendor_id(self, value):
        self._vendor_id = value

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @serial_no.setter
    def serial_no(self, value):
        self._serial_number = value


    def reset_device(self):
        self._vendor_id = ""
        self._manufacturer = ""
        self._serial_number = ""
        self._product_id = ""
