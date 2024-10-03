from adafruit_bus_device.i2c_device import I2CDevice


MAX1720X_I2CADDR = 0x36

MAX1720X_STATUS_ADDR = 0x00  # Contains alert status and chip status
MAX1720X_VCELL_ADDR = 0x09  # Lowest cell voltage of a pack
MAX1720X_REPSOC_ADDR = 0x06  # Reported state of charge
MAX1720X_REPCAP_ADDR = 0x05  # Reported remaining capacity
MAX1720X_TEMP_ADDR = 0x08  # Temperature
MAX1720X_CURRENT_ADDR = 0x0A  # Battery current
MAX1720X_TTE_ADDR = 0x11  # Time to empty
MAX1720X_TTF_ADDR = 0x20  # Time to full
MAX1720X_CAPACITY_ADDR = 0x10  # Full capacity estimation
MAX1720X_VBAT_ADDR = 0xDA  # Battery pack voltage
MAX1720X_AVCELL_ADDR = 0x17  # Battery cycles

MAX1720X_COMMAND_ADDR = 0x60  # Command register
MAX1720X_CONFIG2_ADDR = 0xBB  # Command register
MAX1720X_CFGPACK_ADDR = 0xB5  # nPackCfg register


def unpack_signed_short_int(byte_list):
    """
    Unpacks a signed 2-byte integer from a list of 2 bytes.

    :param byte_list: List of 2 bytes representing the packed 2-byte signed
    integer.
    :return: Unpacked signed 2-byte integer.
    """
    val = (byte_list[1] << 8) | byte_list[0]
    return val if val < 0x8000 else val - 0x10000


class MAX17205():
    def __init__(self, i2c):
        self.i2c_device = I2CDevice(i2c, MAX1720X_I2CADDR)
        self.tx_buffer = bytearray(2)
        self.rx_buffer = bytearray(2)

        self.voltage = 0.0
        self.current = 0.0
        self.midvoltage = 0.0

        self.soc = 0
        self.capacity = 0

    def config_pack(self):
        """
        Configure pack parameters.

        :return: Boolean for success.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_REPSOC_ADDR
            i2c.write(bytes([MAX1720X_CFGPACK_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to an int16
        print(self.rx_buffer)

        return True

    def read_soc(self):
        """
        Reads SoC from the battery pack.

        :return: SoC as a percentage.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_REPSOC_ADDR
            i2c.write(bytes([MAX1720X_REPSOC_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to pack SoC
        self.soc = int.from_bytes(
            self.rx_buffer, 'little', signed=False) / 256

        return self.soc

    def read_capacity(self):
        """
        Reads capacity from the battery pack.

        :return: Capacity in mAh.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_REPCAP_ADDR
            i2c.write(bytes([MAX1720X_REPCAP_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to pack capacity
        self.capacity = int.from_bytes(
            self.rx_buffer, 'little', signed=False) / 256

        return self.capacity

    def read_current(self):
        """
        Reads the current from the battery pack.

        :return: Current in mA as a float.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_CURRENT_ADDR
            i2c.write(bytes([MAX1720X_CURRENT_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to an int16
        current_raw = unpack_signed_short_int(self.rx_buffer)

        # Cast int16 to a float and scale for mA current
        self.current = float(current_raw) * 0.0015625/0.01

        return self.current

    def read_voltage(self):
        """
        Reads the voltage for the battery pack.

        :return: Voltage in mV as a float.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_VBAT_ADDR
            i2c.write(bytes([MAX1720X_VBAT_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to a uint16
        voltage_raw = int.from_bytes(self.rx_buffer, 'little', signed=False)

        # Cast uint16 to a float and scale for mV voltage
        self.voltage = float(voltage_raw) * 1.25

        return self.voltage

    def read_midvoltage(self):
        """
        Reads the midpoint voltage for the battery pack.

        :return: Voltage in mV as a float.
        """
        with self.i2c_device as i2c:
            # Read 2 bytes from MAX1720X_VCELL_ADDR
            i2c.write(bytes([MAX1720X_VCELL_ADDR]))
            i2c.readinto(self.rx_buffer)

        # Convert readback bytes to a uint16
        midvoltage_raw = int.from_bytes(self.rx_buffer, 'little', signed=False)

        # Cast uint16 to a float and scale for mV voltage
        self.midvoltage = float(midvoltage_raw) * 0.078125

        return self.midvoltage
