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
from pathlib import Path
import sys

from hpl.parser import property_parser, specification_parser

from hplrv.rendering import TemplateRenderer

###############################################################################
# Constants
###############################################################################

PROG_GEN: Final[str] = 'hpl-rv gen'

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


def run(args: Dict[str, Any], _settings: Dict[str, Any]) -> int:
    parts: List[str] = []
    if args.get('files'):
        parts.extend(generate_from_files(args['args']))
    else:
        parts.extend(generate_from_properties(args['args']))
    output: str = '\n\n'.join(code for code in parts)

    input_path: str = args.get('output')
    if input_path:
        path: Path = Path(input_path).resolve(strict=False)
        path.write_text(output, encoding='utf-8')
    else:
        print(output)
    return 0


def generate_from_files(paths: List[str]) -> List[str]:
    parser = specification_parser()
    r = TemplateRenderer()
    outputs = []
    for input_path in paths:
        path: Path = Path(input_path).resolve(strict=True)
        text: str = path.read_text(encoding='utf-8').strip()
        spec = parser.parse(text)
        for hpl_property in spec.properties:
            code = r.render_monitor(hpl_property)
            outputs.append(code)
    return outputs


def generate_from_properties(properties: List[str]) -> List[str]:
    parser = property_parser()
    r = TemplateRenderer()
    outputs = []
    for text in properties:
        hpl_property = parser.parse(text)
        code = r.render_monitor(hpl_property)
        outputs.append(code)
    return outputs
