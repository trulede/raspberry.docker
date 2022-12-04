import argparse
from .rfid import rfid_parser
from .switch import switch_parser


def main():
    parser = argparse.ArgumentParser(
        prog='shellylight',
        description='Shelly Light Project',
    )
    subparsers = parser.add_subparsers(help='commands')
    rfid_parser(subparsers.add_parser('rfid', help='RFID Command'))
    switch_parser(subparsers.add_parser('switch', help='Switch Command'))
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
