try:
    from typing import Optional
    from busio import UART
    from circuitpython_typing import ReadableBuffer
except ImportError:
    pass

class GPS:
    def __init__(self, uart: UART, debug: bool = False) -> None:
        self._uart = uart
        self.debug = debug
        self._msg = None
        self._payload_len = 0
        self._msg_id = 0
        self._msg_cs = 0
        self._payload = bytearray([0] * 58)
        self._nav_data = {}

    def update(self) -> bool:
        try:
            msg = self._parse_sentence()
        except UnicodeError:
            return False
        if msg is None or len(msg) < 11:
            return False

        self._msg = [hex(i) for i in msg]
        self._payload_len = ((msg[2] & 0xFF) << 8) | msg[3]
        self._msg_id = msg[4]
        self._msg_cs = msg[-3]
        self._payload = bytearray(int(i, 16) for i in self._msg[4:-3])

        if self._msg_id != 0xA8:
            print("Invalid message ID, expected 0xA8, got: ", hex(self._msg_id))
            return False

        if self.debug:
            print("Raw message: \n", self._msg)
            print("Payload: \n", self._payload)

        cs = 0
        for i in self._payload:
            cs ^= i
        if cs != self._msg_cs:
            print("Checksum failed!")
            return False

        # Populate _nav_data as a dictionary
        self._nav_data = {
            "message_id": self._payload[0],
            "fix_mode": self._payload[1],
            "number_of_sv": self._payload[2],
            "gps_week": (self._payload[3] << 8) | self._payload[4],
            "tow": (self._payload[5] << 24) | (self._payload[6] << 16) | (self._payload[7] << 8) | self._payload[8],
            "latitude": (self._payload[9] << 24) | (self._payload[10] << 16) | (self._payload[11] << 8) | self._payload[12],
            "longitude": (self._payload[13] << 24) | (self._payload[14] << 16) | (self._payload[15] << 8) | self._payload[16],
            "ellipsoid_alt": (self._payload[17] << 24) | (self._payload[18] << 16) | (self._payload[19] << 8) | self._payload[20],
            "mean_sea_lvl_alt": (self._payload[21] << 24) | (self._payload[22] << 16) | (self._payload[23] << 8) | self._payload[24],
            "gdop": (self._payload[25] << 8) | self._payload[26],
            "pdop": (self._payload[27] << 8) | self._payload[28],
            "hdop": (self._payload[29] << 8) | self._payload[30],
            "vdop": (self._payload[31] << 8) | self._payload[32],
            "tdop": (self._payload[33] << 8) | self._payload[34],
            "ecef_x": (self._payload[35] << 24) | (self._payload[36] << 16) | (self._payload[37] << 8) | self._payload[38],
            "ecef_y": (self._payload[39] << 24) | (self._payload[40] << 16) | (self._payload[41] << 8) | self._payload[42],
            "ecef_z": (self._payload[43] << 24) | (self._payload[44] << 16) | (self._payload[45] << 8) | self._payload[46],
            "ecef_vx": (self._payload[47] << 24) | (self._payload[48] << 16) | (self._payload[49] << 8) | self._payload[50],
            "ecef_vy": (self._payload[51] << 24) | (self._payload[52] << 16) | (self._payload[53] << 8) | self._payload[54],
            "ecef_vz": (self._payload[55] << 24) | (self._payload[56] << 16) | (self._payload[57] << 8) | self._payload[58]
        }

        if self.debug:
            print("Nav data: \n", self._nav_data)

        return True

    def get_nav_data(self) -> dict:
        """Returns the current navigation data as a dictionary."""
        return self._nav_data

    def write(self, bytestr: ReadableBuffer) -> Optional[int]:
        return self._uart.write(bytestr)

    def set_to_binary(self) -> None:
        self.write(b"\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A")

    @property
    def in_waiting(self) -> int:
        return self._uart.in_waiting

    def readline(self) -> Optional[bytes]:
        return self._uart.readline()

    def _read_sentence(self) -> Optional[bytes]:
        if self.in_waiting < 11:
            return None
        return self.readline()

    def _parse_sentence(self) -> Optional[bytes]:
        return self._read_sentence()
