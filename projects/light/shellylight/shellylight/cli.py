import types
import argparse
import inspect
from .nfc import register_parser as nfc_register_parser
from .switch import register_parser as switch_register_parser


def register_subparsers(subparsers):
    nfc_register_parser(subparsers)
    switch_register_parser(subparsers)


def main():
    parser = argparse.ArgumentParser(
        prog='shellylight',
        description='Shelly Light Project',
    )
    subparsers = parser.add_subparsers(help='commands')
    register_subparsers(subparsers)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
