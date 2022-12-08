
from time import sleep
import board
import busio
import string
import signal
from digitalio import DigitalInOut
from .pn532.spi import PN532_SPI
from .pn532.pn532 import MIFARE_CMD_AUTH_A


_actions = [
    'On',
    'Off',
    'Bright',
    'Colour',
    'All',
]


_lights = [
    'Main',
    'Side',
    'Bed',
    'Game',
    'All',
]


def register_parser(subparsers):
    rfid_parser(subparsers.add_parser('rfid', help='RFID Command'))


def rfid_parser(subparser):
    subparser.set_defaults(func=rfid_command)
    # Group Listen.
    listen_group = subparser.add_argument_group('Listen')
    listen_group.add_argument('--listen', action='store_true',
            help='Run the RFID Listen function.')
    listen_group.add_argument('--uidonly', action='store_true',
            help='Only dump the Card UID to console.')
    # Group Program.
    program_group = subparser.add_argument_group('Program')
    program_group.add_argument('--program', action='store_true',
            help='Program a Card for the Light Function.')
    program_group.add_argument('--name', type=str,
            help='Program this name on the Card.')
    program_group.add_argument('--actions', choices=_actions, nargs='*',
            help='Configure these actions on the Card.')
    program_group.add_argument('--lights', choices=_lights, nargs='*',
            help='Control these groups of lights with the Card.')
    # Group MQTT.
    mqtt_group = subparser.add_argument_group('MQTT')
    program_group.add_argument('--mqtt', action='store_true',
            help='Monitor the RFID and send MQTT messages when Cards are detected.')
    mqtt_group.add_argument('--broker', type=str, nargs=1,
            help='Send MQTT messages to this MQTT Broker.')


def rfid_command(args):
    if args.listen:
        listen(args.uidonly)


def dump_block(bn, block):
    hex = " ".join([format(i, "02x") for i in block])
    asc = "".join([chr(i) if chr(i) in string.printable else '.' for i in block])
    print(f'  [{bn:02}] {hex}    {asc}')


def signal_handler(sig, frame):
    exit(0)


def listen(uidonly):
    # Setup PN532 with SPI connection.
    print(f'RFID Listen using PN532 with SPI connection ...')
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    pn532 = PN532_SPI(spi, DigitalInOut(board.D4), irq=None, reset=DigitalInOut(board.D20))
    ver = pn532.firmware_version
    print(f'PN532: ic={ver[0]}, ver={ver[1]}, rev={ver[2]}')

    # Enable MiFare cards (i.e. for the supplied blue token).
    pn532.SAM_configuration()
    
    # Listen for cards.
    print('Listening for cards (ctrl-c to exit) ...')
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        # Wait for a card.
        uid = pn532.read_passive_target()
        if not uid:
            continue
        # Have a card, read.
        print(f'Card found, UID={" ".join([format(i, "02x") for i in uid])}')
        if not uidonly:
            print(f'  MiFare Blocks:')
            key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
            for bn in range(64):
                try:
                    pn532.mifare_classic_authenticate_block(
                        uid, block_number=bn,
                        key_number=MIFARE_CMD_AUTH_A, key=key_a)
                    block = pn532.mifare_classic_read_block(bn)
                    if block:
                        dump_block(bn, block)
                    else:
                        break
                except exception as e:
                    print(e)
            print(f'  NTAG Blocks:')
            for bn in range(135):
                block = pn532.ntag2xx_read_block(bn)
                if block:
                    dump_block(bn, block)
                else:
                    break
            if pn532.read_passive_target(timeout=0.1):
                print('Block scan complete.')
        # Wait for the card to be removed.
        while pn532.read_passive_target(timeout=0.2):
            pass
        print('Card removed.')
