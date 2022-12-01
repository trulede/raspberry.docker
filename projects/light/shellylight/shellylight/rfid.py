

def rfid_parser(subparser):
    subparser.add_argument('-r', type=int, default=1)
    subparser.set_defaults(func=rfid_command)


def rfid_command(args):
    print('RFID Command')
    print(args)
