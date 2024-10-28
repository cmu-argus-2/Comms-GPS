"""
GPS message parser.

This module will parse the GPS messages received from the GPS module and return the data.

Author: Adrian Walker
"""

# The GPS data we are looking for is:
# - GPS_MESSAGE_ID              (???)
# - GPS_FIX_MODE            (???)
# - GPS_NUMBER_OF_SV        (???)
# - GPS_GNSS_WEEK           (???)
# - GPS_GNSS_TOW            (???)
# - GPS_LATITUDE
# - GPS_LONGITUDE
# - GPS_ELLIPSOID_ALT
# - GPS_MEAN_SEA_LVL_ALT
# - GPS_GDOP
# - GPS_PDOP
# - GPS_HDOP
# - GPS_VDOP
# - GPS_TDOP
# - GPS_POS_X_ECEF
# - GPS_POS_Y_ECEF
# - GPS_POS_Z_ECEF
# - GPS_VEL_X_ECEF
# - GPS_VEL_Y_ECEF
# - GPS_VEL_Z_ECEF

class GPS_Data:
    """GPS data class.  Contains the parsed GPS data from the GPS module."""

    def __init__(self) -> None:
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.timestamp = None
        self.satellites = None
        self.fix_quality = None
        self.horizontal_dilution = None
        self.antenna_height = None
        self.geoid_height = None
        self.age_of_differential = None
        self.differential_reference = None
        self.checksum = None
