import argparse

from os import path as P

OPT_GENERATE_CONFIG = 'generate-config'
OPT_SERVER = 'server'

# Note dost import any custom module this file


def main():

    parser = argparse.ArgumentParser(add_help=True)

    subparsers = parser.add_subparsers(dest="operation")  # required param not support on python 3.6
    subparsers.add_parser(OPT_GENERATE_CONFIG, help="Generate config template")
    subparsers.add_parser(OPT_SERVER, help="Start web server")

    args_namespace = parser.parse_args()

    operation = args_namespace.operation

    if operation == OPT_GENERATE_CONFIG:
        here = P.dirname(P.abspath(__file__))
        p_config_template = P.join(here, 'cooka_config.py.template')
        with open(p_config_template, 'r') as f:
            content = f.read()
        print(content)
    elif operation == OPT_SERVER:
        # to avoid import output
        from cooka.server import start_server
        start_server()
    else:
        print(parser.format_help())
        exit(-1)


if __name__ == "__main__":
    main()
