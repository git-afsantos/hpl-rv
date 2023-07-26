# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the command line program.

Why does this file exist, and why not put this in __main__?

  In some cases, it is possible to import `__main__.py` twice.
  This approach avoids that. Also see:
  https://click.palletsprojects.com/en/5.x/setuptools/#setuptools-integration

Some of the structure of this file came from this StackExchange question:
  https://softwareengineering.stackexchange.com/q/418600
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional

import argparse
import sys
from traceback import print_exc

from hplrv import __version__ as current_version, gen, gui, play

###############################################################################
# Constants
###############################################################################

PROG: Final[str] = 'hpl-rv'
CMD_GEN: Final[str] = 'gen'
CMD_GUI: Final[str] = 'gui'
CMD_PLAY: Final[str] = 'play'

###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    description = 'Tools to enable Runtime Verification from HPL properties.'
    parser = argparse.ArgumentParser(prog=PROG, description=description)

    parser.add_argument(
        '--version',
        action='version',
        version=f'{PROG} {current_version}',
        help='prints the program version',
    )

    parser.add_argument(
        'cmd',
        metavar='CMD',
        choices=[CMD_GEN, CMD_GUI, CMD_PLAY],
        help=f'a {PROG} command to run',
    )

    parser.add_argument(
        'args',
        metavar='ARG',
        nargs=argparse.REMAINDER,
        help=f'arguments for the {PROG} command',
    )

    args = parser.parse_args(args=argv)
    return vars(args)


###############################################################################
# Setup
###############################################################################


def load_configs(args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        config: Dict[str, Any] = {}
        # with open(args['config_path'], 'r') as file_pointer:
        # yaml.safe_load(file_pointer)

        # arrange and check configs here

        return config
    except Exception as err:
        # log or raise errors
        print(err, file=sys.stderr)
        if str(err) == 'Really Bad':
            raise err

        # Optional: return some sane fallback defaults.
        sane_defaults: Dict[str, Any] = {}
        return sane_defaults


###############################################################################
# Entry Point
###############################################################################


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_arguments(argv)

    try:
        # Load additional config files here, e.g., from a path given via args.
        # Alternatively, set sane defaults if configuration is missing.
        config = load_configs(args)
        cmd: str = args['cmd']

        if cmd == CMD_GEN:
            return gen.subprogram(args.get('args'), config)
        if cmd == CMD_GUI:
            return gui.subprogram(args.get('args'), config)
        if cmd == CMD_PLAY:
            return play.subprogram(args.get('args'), config)

    except KeyboardInterrupt:
        print('Aborted manually.', file=sys.stderr)
        return 1

    except Exception as err:
        print('An unhandled exception crashed the application!')
        print(err)
        print_exc()
        return 1

    return 0  # success
