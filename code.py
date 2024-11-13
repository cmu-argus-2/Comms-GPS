# GPS module demonstration.
# type: ignore
import time
import board
import busio

import digitalio
# import adafruit_gps
import gps_driver

DEBUG = True

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=10)

# Power the GPS module
pin = digitalio.DigitalInOut(board.GPS_EN)
pin.direction = digitalio.Direction.OUTPUT
pin.value = True

# Create a GPS module instance.
# gps = adafruit_gps.GPS(uart, debug=True)  # Use UART/pyserial
gps = gps_driver.GPS(uart, debug=DEBUG)  # Use UART/pyserial

# Wait for 3 seconds to allow the GPS module to boot up
time.sleep(3)
gps.set_to_binary()

# Main loop runs forever printing the location, etc. every second.
last_print = time.monotonic()
while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data (you can ignore it
    # though if you don't care and instead look at the has_fix property).
    updated = gps.update()

    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 1:
        last_print = current
        if gps._nav_data["fix_mode"] == 0:
                print("Waiting for fix...")
                if DEBUG:
                    gps.print_parsed_msg()
                continue
        else:
            print("Updated")
            nav_data = gps.get_nav_data()
            parsed_data = gps.get_parsed_data()
            gps.print_parsed_data()
