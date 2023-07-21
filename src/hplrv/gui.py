# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gui' command line program and the
dashboard server to manage runtime monitors.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional, Set, Type, Union

import argparse
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import pkg_resources
from threading import Event, Lock, Thread

from attrs import field, frozen
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
# Live Monitoring Client
###############################################################################


@frozen
class LiveMonitoringClient:
    host: str
    port: int
    lock: Lock = field(factory=Lock, init=False, eq=False)
    has_started: Event = field(factory=Event, init=False, eq=False)
    monitor_report: List[Dict[str, Any]] = field(factory=list, init=False, eq=False)

    def get_monitor_status(self) -> List[Dict[str, Any]]:
        with self.lock:
            return deepcopy(self.monitor_report)

    def run(self):
        # to be called from the dedicated thread
        self.has_started.set()
        try:
            asyncio.run(self._run_client())
        except asyncio.CancelledError:
            pass

    async def _run_client(self):
        reader, _writer = await asyncio.open_connection(self.host, self.port)
        # read initial status report
        report = await reader.readline()
        with self.lock:
            self.monitor_report = json.loads(report.decode('utf8'))
        # loop to receive live updates
        while True:
            update = await reader.readline()
            verdict = json.loads(update.decode('utf8'))
            self.set_verdict(verdict)

    def set_verdict(self, verdict: Dict[str, Any]):
        i = verdict['monitor']
        with self.lock:
            self.monitor_report[i]['verdict'] = verdict['value']
            self.monitor_report[i]['witness'] = verdict['witness']


###############################################################################
# Public Interface
###############################################################################

# Important note regarding gevent-based servers:
# "... the servers spawn one greenlet per connection (not per request)"

# Normal HTTP requests create a new connection as per the WSGI standard.
# The websocket request is a new connection (of type websocket), so we have
# (h + w) connections going on at any given time (h = HTTP, w = WebSocket),
# meaning that we also have (h + w) greenlets.


@frozen
class MonitorServer:
    app: Bottle
    monitors: List[Dict[str, Any]] = field(factory=list, init=False, eq=False)
    # servers: Set[Any] = field(factory=set, init=False, repr=False, eq=False)
    clients: Set[Any] = field(factory=set, init=False, repr=False, eq=False)
    lock: RLock = field(factory=RLock, init=False, repr=False, eq=False)

    def __attrs_post_init__(self):
        self.app.get('/')(self.index)
        self.app.get('/<filename:path>')(self.send_static_file)
        self.app.get('/ws', apply=[websocket])(self.live_updates)

    def index(self):
        return static_file('index.html', root=CLIENT_ROOT, mimetype='text/html')

    def send_static_file(self, filename):
        return static_file(filename, root=CLIENT_ROOT)

    def live_updates(self, ws):
        with self.lock:
            self.clients.add(ws)
        try:
            pass
            # while True:
            #     msg = ws.receive()
            #     if msg is not None:
            #         for u in users:
            #             u.send(msg)
            #     else:
            #         break
        finally:
            with self.lock:
                self.clients.remove(ws)

    def start_live_monitoring_thread(self):
        thread = Thread(self._live_monitoring_loop, name='live monitoring client', daemon=True)
        thread.start()

    def connect_to_live_server(self, host: str, port: int):
        server = create_connection((host, port))


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
    app = MonitorServer(Bottle())
    gevent.spawn(app.connect_to_live_server, args['rv_server'], args['rv_port'])
    serve_forever(app=app, host=args['host'], port=args['port'], server=GeventWebSocketServer)
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
        default=4242,
        help=f'port of the RV server (default: 5186)',
    )

    args = parser.parse_args(args=argv)
    return vars(args)

