# Comms-GPS

This repo contains the code used on the circuit python board to test the GPS module


## Use

The code is written to run on a CircuitPython board and should be copied onto the board to run.

See the docs folder for dataflow.

### Minimum needed information from the GPS module, per discussion with Akshat Sahay:
- GPS_MESSAGE_ID
- GPS_FIX_MODE
- GPS_NUMBER_OF_SV
- GPS_GNSS_WEEK
- GPS_GNSS_TOW
- GPS_LATITUDE
- GPS_LONGITUDE
- GPS_ELLIPSOID_ALT
- GPS_MEAN_SEA_LVL_ALT
- GPS_GDOP
- GPS_PDOP
- GPS_HDOP
- GPS_VDOP
- GPS_TDOP
- GPS_POS_X_ECEF
- GPS_POS_Y_ECEF
- GPS_POS_Z_ECEF
- GPS_VEL_X_ECEF
- GPS_VEL_Y_ECEF
- GPS_VEL_Z_ECEF