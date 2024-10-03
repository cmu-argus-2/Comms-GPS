import time
import board
import busio
from max1720x import MAX17205


i2c = busio.I2C(board.SCL2, board.SDA2)

max17205 = MAX17205(i2c)

while True:
    print("Voltage:", max17205.read_voltage())
    print("Current:", max17205.read_current())
    print("SoC:", max17205.read_soc())
    print("Capacity:", max17205.read_capacity())
    print("Midpoint Voltage:", max17205.read_midvoltage())
    print()
    time.sleep(3)
