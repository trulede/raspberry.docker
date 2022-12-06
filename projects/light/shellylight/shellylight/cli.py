import types
import argparse


def register_subparsers(module_dict, subparsers):
    for name, value in module_dict.items():
        if name == 'register_parser' and callable(value):
            value(subparsers)
        elif isinstance(value, types.ModuleType):
            register_subparsers(value.__dict__, subparsers)


def main():
    parser = argparse.ArgumentParser(
        prog='shellylight',
        description='Shelly Light Project',
    )
    subparsers = parser.add_subparsers(help='commands')
    register_subparsers(globals(), subparsers)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
