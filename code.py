
# type: ignore
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
# import time
import board
import busio

import digitalio
# import adafruit_gps
import gps_driver
import gps_parser

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=10)

pin = digitalio.DigitalInOut(board.GPS_EN)
pin.direction = digitalio.Direction.OUTPUT
pin.value = True

# Create a GPS module instance.
# gps = adafruit_gps.GPS(uart, debug=True)  # Use UART/pyserial
gps = gps_driver.GPS(uart, debug=True)  # Use UART/pyserial

# Main loop runs forever printing the location, etc. every second.
# last_print = time.monotonic()
while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data (you can ignore it
    # though if you don't care and instead look at the has_fix property).
    gps.update()
    # Every second print out current location details if there's a fix.
    # current = time.monotonic()
    # if current - last_print >= 1.0:
    #     last_print = current
    #     if not gps.data:
    #         # Try again if we don't have a fix yet.
    #         print("Waiting for data...")
    #         continue
    #     # We have a fix! (gps.has_fix is true)
    #     # Print out details about the fix like location, date, etc.
    #     print("=" * 40)  # Print a separator line.
    #     print("GPS data: {0}".format(gps.data))
