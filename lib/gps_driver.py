try:
    from typing import Optional
    from busio import UART
    from circuitpython_typing import ReadableBuffer
    from datetime import datetime, timedelta, timezone
except ImportError:
    pass

EPOCH = datetime(1980, 1, 5, tzinfo=timezone.utc)
try:
    from typing import Optional
    from busio import UART
    from circuitpython_typing import ReadableBuffer
    from datetime import datetime, timedelta, timezone
except ImportError:
    pass

# EPOCH = datetime(1980, 1, 5, tzinfo=timezone.utc)

class GPS:
    def __init__(self, uart: UART, debug: bool = False) -> None:
        self._uart = uart
        self.debug = debug
        self._msg = None
        self._payload_len = 0
        self._msg_id = 0
        self._msg_cs = 0
        self._payload = bytearray([0] * 59)
        self._nav_data = {}
        self.parsed_data = {}

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
            #print("Message content: \n", self._msg)
            return False

        if self._payload_len != 59:
            print("Invalid payload length, expected 59, got: ", self._payload_len)
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

        _ = self.parse_data()

        return True


    def parse_fix_mode(self) -> str:
        if self._nav_data["fix_mode"] == 0:
            return "No fix"
        if self._nav_data["fix_mode"] == 1:
            return "2D fix"
        elif self._nav_data["fix_mode"] == 2:
            return "3D fix"
        else:
            return "3D + DGNSS fix"


    def parse_tow(self) -> int:
        # Convert from 0.01 seconds to seconds
        total_seconds = self._nav_data["tow"] / 100

        # Calculate day of the week
        days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_index = int(total_seconds // 86400) % 7
        day_of_week = days_of_week[day_index]

        # Calculate hours, minutes, and seconds
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60

        # Format the output
        time_of_week = f"{day_of_week}, {hours:02}:{minutes:02}:{seconds:05.2f} (hh:mm:ss.ss)"
        return time_of_week


    def parse_lat(self) -> float:
        # Convert from scale 1/1e-7 to decimal degrees
        latitude = self._nav_data["latitude"] * 1e-7

        # Determine North or South
        direction = "N" if latitude >= 0 else "S"
        latitude = abs(latitude)

        # Convert to degrees, minutes, and seconds
        degrees = int(latitude)
        minutes = int((latitude - degrees) * 60)
        seconds = (latitude - degrees - minutes / 60) * 3600

        # Format output
        latitude_str = f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"
        return latitude_str


    def parse_lon(self) -> float:
        # Convert from scale 1/1e-7 to decimal degrees
        longitude = self._nav_data["longitude"] * 1e-7

        # Determine East or West
        direction = "E" if longitude >= 0 else "W"
        longitude = abs(longitude)

        # Convert to degrees, minutes, and seconds
        degrees = int(longitude)
        minutes = int((longitude - degrees) * 60)
        seconds = (longitude - degrees - minutes / 60) * 3600

        # Format output
        longitude_str = f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"
        return longitude_str


    def parse_elip_alt(self) -> float:
        # Convert from hundredths of a meter to meters
        distance_meters = self._nav_data["ellipsoid_alt"] / 100

        # Format output
        distance_str = f"{distance_meters:.2f} m"
        return distance_str


    def parse_msl_alt(self) -> float:
        # Convert from hundredths of a meter to meters
        distance_meters = self._nav_data["mean_sea_lvl_alt"] / 100

        # Format output
        distance_str = f"{distance_meters:.2f} m"
        return distance_str


    def parse_gdop(self) -> float:
        return (self._nav_data["gdop"]*0.01)


    def parse_pdop(self) -> float:
        return (self._nav_data["pdop"]*0.01)


    def parse_hdop(self) -> float:
        return (self._nav_data["hdop"]*0.01)


    def parse_vdop(self) -> float:
        return (self._nav_data["vdop"]*0.01)


    def parse_tdop(self) -> float:
        return (self._nav_data["tdop"]*0.01)


    def parse_ecef_x(self) -> float:
        # Convert from hundredths of a meter to meters
        distance_meters = self._nav_data["ecef_x"] / 100

        # Format output
        distance_str = f"{distance_meters:.2f} m"
        return distance_str


    def parse_ecef_y(self) -> float:
        # Convert from hundredths of a meter to meters
        distance_meters = self._nav_data["ecef_y"] / 100

        # Format output
        distance_str = f"{distance_meters:.2f} m"
        return distance_str


    def parse_ecef_z(self) -> float:
        # Convert from hundredths of a meter to meters
        distance_meters = self._nav_data["ecef_z"] / 100

        # Format output
        distance_str = f"{distance_meters:.2f} m"
        return distance_str


    def parse_ecef_vx(self) -> float:
        # Convert from hundredths of a meter to meters
        speed_meters = self._nav_data["ecef_vx"] / 100

        # Format output
        speed_meters = f"{speed_meters:.2f} m/s"
        return speed_meters


    def parse_ecef_vy(self) -> float:
        # Convert from hundredths of a meter to meters
        speed_meters = self._nav_data["ecef_vy"] / 100

        # Format output
        speed_meters = f"{speed_meters:.2f} m/s"
        return speed_meters


    def parse_ecef_vz(self) -> float:
        # Convert from hundredths of a meter to meters
        speed_meters = self._nav_data["ecef_vz"] / 100

        # Format output
        speed_meters = f"{speed_meters:.2f} m/s"
        return speed_meters


    # def gps_datetime(gps_week: int, tow: int) -> float:
    #     """Get the unix time from GPS week and TOW (time of week)."""
    #     usec = tow % 100 * 1000
    #     # 86400 is number of seconds in a day
    #     sec = (tow / 100) % 86400
    #     day = ((tow / 100) / 86400) + (gps_week * 7)
    #     dt = EPOCH + timedelta(days=day, seconds=sec, microseconds=usec)
    #     return dt.timestamp()


    def parse_data(self) -> dict:
        if not self._nav_data:
            return
        fix = self.parse_fix_mode()
        sv_count = self._nav_data["number_of_sv"]
        gnss_week = self._nav_data["gps_week"]
        tow = self.parse_tow()
        lat = self.parse_lat()
        lon = self.parse_lon()
        elip_alt = self.parse_elip_alt()
        msl_alt = self.parse_msl_alt()
        gdop = self.parse_gdop()
        pdop = self.parse_pdop()
        hdop = self.parse_hdop()
        vdop = self.parse_vdop()
        tdop = self.parse_tdop()
        ecef_x = self.parse_ecef_x()
        ecef_y = self.parse_ecef_y()
        ecef_z = self.parse_ecef_z()
        ecef_vx = self.parse_ecef_vx()
        ecef_vy = self.parse_ecef_vy()
        ecef_vz = self.parse_ecef_vz()
        # dt = self.gps_datetime(gnss_week, tow)

        self.parsed_data = {
            "message_id": self._nav_data["message_id"],
            "fix_mode": fix,
            "number_of_sv": sv_count,
            "gps_week": gnss_week,
            "tow": tow,
            "latitude": lat,
            "longitude": lon,
            "ellipsoid_alt": elip_alt,
            "mean_sea_lvl_alt": msl_alt,
            "gdop": gdop,
            "pdop": pdop,
            "hdop": hdop,
            "vdop": vdop,
            "tdop": tdop,
            "ecef_x": ecef_x,
            "ecef_y": ecef_y,
            "ecef_z": ecef_z,
            "ecef_vx": ecef_vx,
            "ecef_vy": ecef_vy,
            "ecef_vz": ecef_vz
            # , "datetime": dt
        }
        return self.parsed_data


    def print_parsed_data(self):
        print("Parsed Data:")
        print("=" * 40)
        for key, value in self.parsed_data.items():
            print(f"{str(key)}: {value}")
        print("=" * 40)


    def get_parsed_data(self) -> dict:
        """Returns the parsed data as a dictionary."""
        return self.parsed_data


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
        self.parsed_data = {}

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
            print("Message content: \n", self._msg)
            return False

        if self._payload_len != 58:
            print("Invalid payload length, expected 58, got: ", self._payload_len)
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

        self.parse_data()

        return True


    def parse_fix_mode(self) -> str:
        if self._nav_data["fix_mode"] == 0:
            return "No fix"
        if self._nav_data["fix_mode"] == 1:
            return "2D fix"
        elif self._nav_data["fix_mode"] == 2:
            return "3D fix"
        else:
            return "3D + DGNSS fix"


    def parse_tow(self) -> int:
        return (self._nav_data["tow"]*0.01)


    def parse_lat(self) -> float:
        return (self._nav_data["latitude"]*0.0000001)

    def parse_lon(self) -> float:
        return (self._nav_data["longitude"]*0.0000001)


    def parse_elip_alt(self) -> float:
        return (self._nav_data["ellipsoid_alt"]*0.01)


    def parse_msl_alt(self) -> float:
        return (self._nav_data["mean_sea_lvl_alt"]*0.01)


    def parse_gdop(self) -> float:
        return (self._nav_data["gdop"]*0.01)


    def parse_pdop(self) -> float:
        return (self._nav_data["pdop"]*0.01)


    def parse_hdop(self) -> float:
        return (self._nav_data["hdop"]*0.01)


    def parse_vdop(self) -> float:
        return (self._nav_data["vdop"]*0.01)


    def parse_tdop(self) -> float:
        return (self._nav_data["tdop"]*0.01)


    def parse_ecef_x(self) -> float:
        return (self._nav_data["ecef_x"]*0.01)


    def parse_ecef_y(self) -> float:
        return (self._nav_data["ecef_y"]*0.01)


    def parse_ecef_z(self) -> float:
        return (self._nav_data["ecef_z"]*0.01)


    def parse_ecef_vx(self) -> float:
        return (self._nav_data["ecef_vx"]*0.01)


    def parse_ecef_vy(self) -> float:
        return (self._nav_data["ecef_vy"]*0.01)


    def parse_ecef_vz(self) -> float:
        return (self._nav_data["ecef_vz"]*0.01)


    def gps_datetime(gps_week: int, tow: int) -> float:
        """Get the unix time from GPS week and TOW (time of week)."""
        usec = tow % 100 * 1000
        # 86400 is number of seconds in a day
        sec = (tow / 100) % 86400
        day = ((tow / 100) / 86400) + (gps_week * 7)
        dt = EPOCH + timedelta(days=day, seconds=sec, microseconds=usec)
        return dt.timestamp()


    def parse_data(self) -> dict:
        if not self._nav_data:
            return
        fix = self.parse_fix_mode()
        sv_count = self._nav_data["number_of_sv"]
        gnss_week = self._nav_data["gps_week"]
        tow = self.parse_tow()
        lat = self.parse_lat()
        lon = self.parse_lon()
        elip_alt = self.parse_elip_alt()
        msl_alt = self.parse_msl_alt()
        gdop = self.parse_gdop()
        pdop = self.parse_pdop()
        hdop = self.parse_hdop()
        vdop = self.parse_vdop()
        tdop = self.parse_tdop()
        ecef_x = self.parse_ecef_x()
        ecef_y = self.parse_ecef_y()
        ecef_z = self.parse_ecef_z()
        ecef_vx = self.parse_ecef_vx()
        ecef_vy = self.parse_ecef_vy()
        ecef_vz = self.parse_ecef_vz()
        dt = self.gps_datetime(gnss_week, tow)

        self.parsed_data = {
            "message_id": self._nav_data["message_id"],
            "fix_mode": fix,
            "number_of_sv": sv_count,
            "gps_week": gnss_week,
            "tow": tow,
            "latitude": lat,
            "longitude": lon,
            "ellipsoid_alt": elip_alt,
            "mean_sea_lvl_alt": msl_alt,
            "gdop": gdop,
            "pdop": pdop,
            "hdop": hdop,
            "vdop": vdop,
            "tdop": tdop,
            "ecef_x": ecef_x,
            "ecef_y": ecef_y,
            "ecef_z": ecef_z,
            "ecef_vx": ecef_vx,
            "ecef_vy": ecef_vy,
            "ecef_vz": ecef_vz,
            "datetime": dt
        }
        return self.parsed_data


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
