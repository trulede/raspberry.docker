import types
import argparse
import inspect
from shellylight import *


def register_subparsers(subparsers):
    for k, v in inspect.getmembers(shellylight, predicate=inspect.ismodule):
        print(k)
        for name, func in inspect.getmembers(v, predicate=inspect.isfunction):
            print(name)
            if name == 'register_parser':
                func(subparsers)


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
