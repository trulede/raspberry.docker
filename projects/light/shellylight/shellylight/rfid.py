
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
            default=[], help='Configure these actions on the Card.')
    program_group.add_argument('--lights', choices=_lights, nargs='*',
            default=[], help='Control these groups of lights with the Card.')
    # Group MQTT.
    mqtt_group = subparser.add_argument_group('MQTT')
    program_group.add_argument('--mqtt', action='store_true',
            help='Monitor the RFID and send MQTT messages when Cards are detected.')
    mqtt_group.add_argument('--broker', type=str, nargs=1,
            help='Send MQTT messages to this MQTT Broker.')


def encode_actions(actions):
    if 'All' in actions:
        actions = _actions
        actions.remove('All')
    encoding = ','.join([v[:2] for v in actions])
    return encoding


def encode_lights(lights):
    if 'All' in lights:
        lights = _lights
        lights.remove('All')
    encoding = ','.join([v[:2] for v in lights])
    return encoding


def rfid_command(args):
    if args.listen:
        listen(args.uidonly)
    elif args.program:
        program(name=args.name, actions=args.actions, lights=args.lights)


def dump_block(bn, block):
    if not block:
        return
    hex = " ".join([format(i, "02x") for i in block])
    asc = "".join([chr(i) if chr(i) in string.printable else '.' for i in block])
    print(f'  [{bn:02}] {hex}    {asc}')


def write_block(pn532, uid, bn, block):
    data = bytes(block, 'ascii')
    data = (data + b' '*16)[:16]
    print(f' write {data} @ {bn}')
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    try:
        pn532.mifare_classic_authenticate_block(
            uid, block_number=bn,
            key_number=MIFARE_CMD_AUTH_A, key=key_a)
        block = pn532.mifare_classic_write_block(bn, data)
        return block
    except Exception as e:
        print(e)
    return None


def read_block(pn532, uid, bn):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    try:
        pn532.mifare_classic_authenticate_block(
            uid, block_number=bn,
            key_number=MIFARE_CMD_AUTH_A, key=key_a)
        block = pn532.mifare_classic_read_block(bn)
        return block
    except Exception as e:
        print(e)
    return None


def signal_handler(sig, frame):
    exit(0)


def setup_pn532():
    # Setup PN532 with SPI connection.
    print(f'RFID Listen using PN532 with SPI connection ...')
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    pn532 = PN532_SPI(spi, DigitalInOut(board.D4), irq=None, reset=DigitalInOut(board.D20))
    ver = pn532.firmware_version
    print(f'PN532: ic={ver[0]}, ver={ver[1]}, rev={ver[2]}')

    # Enable MiFare cards (i.e. for the supplied blue token).
    pn532.SAM_configuration()

    return pn532


def wait_for_card(pn532):
    print('Listening for cards (ctrl-c to exit) ...')
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        # Wait for a card.
        uid = pn532.read_passive_target()
        if not uid:
            continue
        # Have a card, read.
        print(f'Card found, UID={" ".join([format(i, "02x") for i in uid])}')
        return uid

    return None  # Code never hit.


def wait_for_no_card(pn532):
    while pn532.read_passive_target(timeout=0.2):
        pass
    print('Card removed.')


def listen(uidonly):
    pn532 = setup_pn532()
    while True:
        # Listen for cards.
        uid = wait_for_card(pn532)
        if uid:
            # Read Blocks
            if not uidonly:
                print(f'  MiFare Blocks:')
                key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
                for bn in range(16):
                    block = read_block(pn532, uid, bn)
                    dump_block(bn, block)
            # Wait for the card to be removed.
            wait_for_no_card(pn532)


def program(name=None, actions=None, lights=[None]):
    pn532 = setup_pn532()

    # Listen for cards.
    uid = wait_for_card(pn532)
    if uid:
        # Don't write to blocks 4N+3 (3, 7 ..) as they contain block passwords.
        # Program the Name (block 6).
        if name:
            write_block(pn532, uid, 6, name)
        # Program the Actions (block 8).
        write_block(pn532, uid, 8, encode_actions(actions))
        # Program the Lights (block 9).
        write_block(pn532, uid, 9, encode_lights(lights))
        # Read back the blocks.
        for bn in (6,8,9):
            block = read_block(pn532, uid, bn)
            dump_block(bn, block)

        # Wait for the card to be removed.
        wait_for_no_card(pn532)
