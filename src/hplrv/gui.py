# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gui' command line program and the
dashboard server to manage runtime monitors.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional, Type, Union

import argparse
from pathlib import Path
import pkg_resources

from attrs import frozen
from bottle import Bottle, run as serve_forever, static_file
from bottle.ext.websocket import GeventWebSocketServer, websocket

# from hpl.ast import HplProperty, HplSpecification
# from hpl.parser import property_parser, specification_parser

###############################################################################
# Constants
###############################################################################

PROG_GUI: Final[str] = 'hpl-rv gui'

CLIENT_ROOT: Final[str] = str(
    Path(pkg_resources.resource_filename('hplrv', 'dashboard/index.html'))
    .resolve(strict=True)
    .parent
)

###############################################################################
# Public Interface
###############################################################################


@frozen
class MonitorServer:
    app: Bottle

    def __attrs_post_init__(self):
        self.app.get('/')(self.index)
        self.app.get('/<filename:path>')(self.send_static_file)
        self.app.get('/ws', apply=[websocket])(self.live_updates)

    def index(self):
        return static_file('index.html', root=CLIENT_ROOT, mimetype='text/html')

    def send_static_file(self, filename):
        return static_file(filename, root=CLIENT_ROOT)

    def live_updates(self, ws):
        # users.add(ws)
        # while True:
        #     msg = ws.receive()
        #     if msg is not None:
        #         for u in users:
        #             u.send(msg)
        #     else:
        #         break
        # users.remove(ws)
        pass


###############################################################################
# Bottle Configuration
###############################################################################


###############################################################################
# Entry Point
###############################################################################


def subprogram(
    argv: Optional[List[str]],
    _settings: Optional[Dict[str, Any]] = None,
) -> int:
    args = parse_arguments(argv)
    return run(args, _settings or {})


def run(args: Dict[str, Any], _settings: Dict[str, Any]) -> int:
    serve_forever(host=args['host'], port=args['port'], server=GeventWebSocketServer)
    return 0


###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    description = 'Dashboard to manage runtime monitors.'
    parser = argparse.ArgumentParser(prog=PROG_GUI, description=description)

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='address of the HTTP server (default: 127.0.0.1)'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=8080,
        help=f'port of the HTTP server (default: 8080)',
    )

    parser.add_argument(
        '--rv-server',
        default='127.0.0.1',
        help='address of the RV server (default: 127.0.0.1)'
    )

    parser.add_argument(
        '--rv-port',
        type=int,
        default=5186,
        help=f'port of the RV server (default: 5186)',
    )

    args = parser.parse_args(args=argv)
    return vars(args)

