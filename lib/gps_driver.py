# Very much simplified version of Adafruit's GPS library

import time
from micropython import const

try:
    from typing import Optional, Tuple, List
    from typing_extensions import Literal
    from circuitpython_typing import ReadableBuffer
    from busio import UART, I2C
except ImportError:
    pass

class GPS:
    """GPS parsing module.  Can parse simple NMEA data sentences from serial
    GPS modules to read latitude, longitude, and more.
    """

    # lint warning about too many statements disabled
    # pylint: disable-msg=R0915
    def __init__(self, uart: UART, debug: bool = False) -> None:
        self._uart = uart
        self.data = None
        self.debug = debug


    def update(self) -> bool:
        """Check for updated data from the GPS module and process it
        accordingly.  Returns True if new data was processed, and False if
        nothing new was received.
        """

        try:
            sentence = self._parse_sentence()
        except UnicodeError:
            return None
        if sentence is None:
            return False
        if self.debug:
            print("=" * 40)
            print(sentence)
            print("-" * 40)
        self.data = sentence
        return True

    @property
    def in_waiting(self) -> int:
        """Returns number of bytes available in UART read buffer"""
        return self._uart.in_waiting

    def readline(self) -> Optional[bytes]:
        """Returns a newline terminated bytestring, must have timeout set for
        the underlying UART or this will block forever!"""
        return self._uart.readline()

    def _read_sentence(self) -> Optional[str]:
        if self.in_waiting < 11:
            return None

        sentence = self.readline()
        return sentence

    def _parse_sentence(self) -> Optional[str]:
        sentence = self._read_sentence()

        return sentence

