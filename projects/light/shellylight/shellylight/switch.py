

def switch_parser(subparser):
    subparser.add_argument('-s', type=int, default=2)
    subparser.set_defaults(func=switch_command)


def switch_command(args):
    print('Switch Command')
    print(args)
