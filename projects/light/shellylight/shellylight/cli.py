import argparse
from .rfid import rfid_parser
from .switch import switch_parser


def main():
    print('Shelly Light Project: CLI')
    parser = argparse.ArgumentParser(description='Shelly Light Project')
    subparsers = parser.add_subparsers()
    rfid_parser(subparsers.add_parser('rfid'))
    switch_parser(subparsers.add_parser('switch'))
    args = parser.parse_args()


if __name__ == "__main__":
    main()
