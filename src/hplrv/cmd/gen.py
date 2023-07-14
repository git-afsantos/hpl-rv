# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gen' command line program.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional

import argparse
import sys

###############################################################################
# Constants
###############################################################################

PROG_GEN: Final[str] = 'hplrv gen'

###############################################################################
# Entry Point
###############################################################################


def subprogram(argv: Optional[List[str]], settings: Dict[str, Any]) -> int:
    args = parse_arguments(argv)
    return run(args, settings)


###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    description = 'Generate runtime monitors from HPL properties.'
    parser = argparse.ArgumentParser(prog=PROG_GEN, description=description)

    parser.add_argument('-o', '--output', help='output file to place generated code')

    parser.add_argument(
        '-f',
        '--files',
        action='store_true',
        help=f'process args as HPL files (default: HPL properties)',
    )

    parser.add_argument('args', nargs='+', help='input properties')

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
# Command
###############################################################################


def run(args: Dict[str, Any], settings: Dict[str, Any]) -> int:
    # https://github.com/git-afsantos/hpl-rv-gen/blob/main/scripts/main.py
    return 0
