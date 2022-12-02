# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


import time
import board
import busio
from digitalio import DigitalInOut
from shellylight.pn532.spi import PN532_SPI


# SPI connection.
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards.
pn532.SAM_configuration()

# Start listening for a card.
print("Waiting for RFID/NFC card...")
while True:
    pn532.listen_for_passive_target()
    if irq_pin.value == 0:
        uid = pn532.get_passive_target()
        print("Found card with UID:", [hex(i) for i in uid])
    else:
        print(".", end="")
    time.sleep(0.1)
