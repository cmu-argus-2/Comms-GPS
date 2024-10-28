"""
GPS message receiver.

This module will receive GPS messages from a serial UART and save their data
to their respective message type fields.

It may be necessary to add sending commands too.

Author: Adrian Walker
"""

try:
    from typing import Optional, Tuple, List
    from typing_extensions import Literal
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
        self.debug = debug
        self._GPGGA = None
        self._GNGLL = None
        self._GNGSA = None
        self._GPGSV = None
        self._GLGSV = None
        self._GAGSV = None
        self._GBGSV = None
        self._GNRMC = None
        self._GNVTG = None
        self._GNZDA = None


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
            print("Raw sentence:")
            print(sentence)

        if sentence.startswith(b"$GPGGA"):
            self._GPGGA = sentence
        elif sentence.startswith(b"$GNGLL"):
            self._GNGLL = sentence
        elif sentence.startswith(b"$GNGSA"):
            self._GNGSA = sentence
        elif sentence.startswith(b"$GPGSV"):
            self._GPGSV = sentence
        elif sentence.startswith(b"$GLGSV"):
            self._GLGSV = sentence
        elif sentence.startswith(b"$GAGSV"):
            self._GAGSV = sentence
        elif sentence.startswith(b"$GBGSV"):
            self._GBGSV = sentence
        elif sentence.startswith(b"$GNRMC"):
            self._GNRMC = sentence
        elif sentence.startswith(b"$GNVTG"):
            self._GNVTG = sentence
        elif sentence.startswith(b"$GNZDA"):
            self._GNZDA = sentence
        else:
            if self.debug:
                print("Unknown sentence")

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

