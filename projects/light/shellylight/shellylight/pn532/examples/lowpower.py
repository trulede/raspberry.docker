# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


import time
import board
import busio
from digitalio import DigitalInOut
from shellylight.pn532.spi import PN532_SPI


# SPI connection:
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

print("Waiting for RFID/NFC card...")
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print("Found card with UID:", [hex(i) for i in uid])
    else:
        print(".", end="")
    pn532.power_down()
    time.sleep(1.0)
