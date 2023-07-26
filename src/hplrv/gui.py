# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gui' command line program and the
dashboard server to manage runtime monitors.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Callable, Dict, Final, List, Optional, Set, Tuple, Type

import argparse
import json
from pathlib import Path
import pkg_resources

from attrs import define, field, frozen
from bottle import Bottle, request, response, run as serve_forever, static_file
from bottle.ext.websocket import GeventWebSocketServer, websocket
import gevent
from gevent.queue import Queue
from gevent.socket import create_connection, socket

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

WS_UPDATE_CB_TYPE: Final[Type] = Callable[[Dict[str, Any]], None]

COMPACT: Final[Tuple[str, str]] = (',', ':')


def noop(*args, **kwargs):
    pass


###############################################################################
# Live Monitoring Client/Server
###############################################################################


@define
class SocketStreamReader:
    # taken from
    # https://stackoverflow.com/a/65637828

    _sock: socket
    _recv_buffer: bytearray = field(factory=bytearray, init=False, eq=False)

    def read(self, num_bytes: int = -1) -> bytes:
        raise NotImplementedError

    def readline(self) -> str:
        return self.readuntil(b'\n').decode('utf8')

    def readuntil(self, separator: bytes = b'\n') -> bytes:
        if len(separator) != 1:
            raise ValueError('Only separators of length 1 are supported.')

        chunk = bytearray(4096)
        start = 0
        buf = bytearray(len(self._recv_buffer))
        bytes_read = self._recv_into(memoryview(buf))
        assert bytes_read == len(buf)

        while True:
            idx = buf.find(separator, start)
            if idx != -1:
                break

            start = len(self._recv_buffer)
            bytes_read = self._recv_into(memoryview(chunk))
            buf += memoryview(chunk)[:bytes_read]

        result = bytes(buf[: idx + 1])
        self._recv_buffer = b''.join(
            (memoryview(buf)[idx + 1 :], self._recv_buffer)
        )
        return result

    def _recv_into(self, view: memoryview) -> int:
        bytes_read = min(len(view), len(self._recv_buffer))
        view[:bytes_read] = self._recv_buffer[:bytes_read]
        self._recv_buffer = self._recv_buffer[bytes_read:]
        if bytes_read == len(view):
            return bytes_read
        bytes_read += self._sock.recv_into(view[bytes_read:])
        return bytes_read


@frozen
class LiveMonitoringServer:
    """
    A gevent greenlet to handle live monitoring status updates.
    If handling multiple multiple live monitoring sources, it is
    preferred to use a shared `updates` queue to make waiting easier.
    """

    host: str
    port: int
    on_update: WS_UPDATE_CB_TYPE = field(default=noop, eq=False, order=False)
    monitors: List[Dict[str, Any]] = field(factory=list, init=False, eq=False, order=False)
    _socket: Optional[socket] = field(default=None, init=False, eq=False, order=False)

    @property
    def is_connected(self) -> bool:
        return self._socket is not None

    def connect(self):
        if self._socket is None:
            s = create_connection((self.host, self.port))
            object.__setattr__(self, "_socket", s)

    def run(self):
        try:
            with self._socket:
                reader = SocketStreamReader(self._socket)

                # read initial monitor report
                data = reader.readline()
                if not data:
                    return
                self.monitors.clear()
                self.monitors.extend(json.loads(data))
                self.push_status()

                # read status updates
                data = reader.readline()
                while data:
                    verdict = json.loads(data)
                    self.push_verdict(verdict)
                    data = reader.readline()
        finally:
            object.__setattr__(self, "_socket", None)

    def push_status(self):
        for i in range(len(self.monitors)):
            monitor = self.monitors[i]
            self.on_update({
                'server': f'{self.host}:{self.port}',
                'id': i,
                'monitor': monitor,
            })

    def push_verdict(self, verdict: Dict[str, Any]):
        i = verdict['monitor']
        monitor = self.monitors[i]
        monitor['verdict'] = verdict['value']
        monitor['witness'] = verdict['witness']
        self.on_update({
            'server': f'{self.host}:{self.port}',
            'id': i,
            'monitor': monitor,
        })

    def asdict(self) -> Dict[str, Any]:
        return {
            'host': self.host,
            'port': self.port,
        }


@frozen
class LiveMonitoringClient:
    websocket: Any
    updates: Queue = field(factory=Queue, init=False, eq=False, order=False)

    def send_initial_server_status(self, host: str, port: int, monitors: List[Dict[str, Any]]):
        server: str = f'{host}:{port}'
        for i in range(len(monitors)):
            monitor = monitors[i]
            data = {
                'server': server,
                'id': i,
                'monitor': monitor,
            }
            self.send_monitor_status(data)

    def get_and_send_update(self):
        status = self.updates.get()
        self.send_monitor_status(status)

    def send_monitor_status(self, status: Dict[str, Any]):
        self.websocket.send(json.dumps(status, separators=COMPACT))


###############################################################################
# Public Interface
###############################################################################

# Important note regarding gevent-based servers:
# "... the servers spawn one greenlet per connection (not per request)"

# Normal HTTP requests create a new connection as per the WSGI standard.
# The websocket request is a new connection (of type websocket), so we have
# (h + w) connections going on at any given time (h = HTTP, w = WebSocket),
# meaning that we also have (h + w) greenlets.

# Greenlets:
# - main server loop?
# - one per HTTP request (automatic cleanup)
# - one per websocket (loop)
# - one per live monitoring server socket (loop)


@frozen
class MonitorServer:
    app: Bottle
    servers: Set[LiveMonitoringServer] = field(factory=set, init=False, eq=False, order=False)
    clients: Set[LiveMonitoringClient] = field(factory=set, init=False, eq=False, order=False)

    def __attrs_post_init__(self):
        self.app.get('/')(self.index)
        self.app.get('/<filename:path>')(self.send_static_file)
        self.app.post('/live')(self.connect_to_live_server)
        self.app.get('/ws', apply=[websocket])(self.live_updates)

    def index(self):
        return static_file('index.html', root=CLIENT_ROOT, mimetype='text/html')

    def send_static_file(self, filename):
        return static_file(filename, root=CLIENT_ROOT)

    def live_updates(self, ws):
        client = LiveMonitoringClient(ws)
        self.clients.add(client)
        try:
            # send initial status reports
            for server in self.servers:
                client.send_initial_server_status(server.host, server.port, server.monitors)
            while True:
                client.get_and_send_update()
        finally:
            self.clients.remove(client)

    def connect_to_live_server(self):
        # host: str = request.forms.get('host')
        # port: int = int(request.forms.get('port'))
        host: str = request.json.get('host')
        port: int = request.json.get('port')
        server = LiveMonitoringServer(host, port, on_update=self._on_live_server_update)
        if server in self.servers:
            return { 'servers': [s.asdict() for s in self.servers] }
        try:
            server.connect()
        except (OSError, ConnectionRefusedError) as e:
            # abort(502, 'Unable to connect to live monitoring server.')
            response.status = 502  # Bad Gateway
            return { 'error': repr(e) }
        else:
            self.servers.add(server)
            gevent.spawn(self._handle_live_server, server)
            return { 'servers': [s.asdict() for s in self.servers] }

    def _handle_live_server(self, server: LiveMonitoringServer):
        try:
            server.run()
        finally:
            self.servers.remove(server)

    def _on_live_server_update(self, update):
        # broadcast to all clients
        for client in self.clients:
            client.updates.put(update)


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
    # TODO use gevent.kill(greenlet) or gevent.killall(greenlets, block=True, timeout=None)
    # with KeyboardInterrupt to kill all ongoing greenlets.
    server = MonitorServer(Bottle())
    serve_forever(app=server.app, host=args['host'], port=args['port'], server=GeventWebSocketServer)
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

    args = parser.parse_args(args=argv)
    return vars(args)
