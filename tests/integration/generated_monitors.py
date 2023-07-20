# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

import asyncio
from collections import deque, namedtuple
from copy import deepcopy
from functools import partial
import json
from math import (
    acos,
    asin,
    atan,
    atan2,
    ceil,
    cos,
    degrees,
    e as E,
    floor,
    log,
    log10,
    pi as PI,
    radians,
    sin,
    sqrt,
    tan,
)
from threading import Lock, Thread

###############################################################################
# Constants and Data Structures
###############################################################################

INF = float("inf")
NAN = float("nan")

COMPACT = (',', ':')

MsgRecord = namedtuple('MsgRecord', ('topic', 'timestamp', 'msg'))

Verdict = namedtuple('Verdict', ('value', 'monitor', 'timestamp', 'witness'))


###############################################################################
# Helper Functions
###############################################################################


def noop(*args, **kwargs):
    pass


def prod(iterable):
    x = 1
    for y in iterable:
        x = x * y
        if x == 0:
            return 0
    return x


def _verdict_to_json(verdict):
    witness = _witness_to_json(verdict.witness)
    return {
        'value': verdict.value,
        'monitor': verdict.monitor,
        'timestamp': verdict.timestamp,
        'witness': witness,
    }

def _witness_to_json(witness):
    data = []
    for record in witness:
        data.append({
            'topic': record.topic,
            'timestamp': record.timestamp,
            'messsage': repr(record.msg),
        })
    return data


###############################################################################
# Monitor Classes
###############################################################################


class Property0Monitor:
    __slots__ = (
        '_lock',          # concurrency control
        '_state',         # currently active state
        'witness',        # MsgRecord list of observed events
        'on_enter_scope', # callback upon entering the scope
        'on_exit_scope',  # callback upon exiting the scope
        'on_violation',   # callback upon verdict of False
        'on_success',     # callback upon verdict of True
        'time_launch',    # when was the monitor launched
        'time_shutdown',  # when was the monitor shutdown
        'time_state',     # when did the last state transition occur
        'cb_map',         # mapping of topic names to callback functions
    )

    PROP_ID = 'None'
    PROP_TITLE = '''None'''
    PROP_DESC = '''None'''
    HPL_PROPERTY = r'''globally: no /a { (x < 0) }'''

    def __init__(self):
        self._lock = Lock()
        self._reset()
        self.on_enter_scope = self._noop
        self.on_exit_scope = self._noop
        self.on_violation = self._noop
        self.on_success = self._noop
        self._state = 0
        self.cb_map = {
            '/a': self.on_msg__a,
        }

    @property
    def verdict(self):
        # with self._lock:
        s = self._state
        if s == -1:
            return True
        if s == -2:
            return False
        return None

    @property
    def is_online_state(self):
        # with self._lock:
        s = self._state
        return s != 0

    @property
    def is_inactive_state(self):
        # with self._lock:
        return self._state == 1

    @property
    def is_active_state(self):
        # with self._lock:
        return self._state == 2

    @property
    def is_safe_state(self):
        # with self._lock:
        return self._state == 3

    @property
    def is_falsifiable_state(self):
        # with self._lock:
        return self._state == 2

    def on_launch(self, stamp):
        with self._lock:
            if self._state != 0:
                raise RuntimeError('monitor is already turned on')
            self._reset()
            self.time_launch = stamp
            self._state = MonitorState.ACTIVE
            self.time_state = stamp
            self.on_enter_scope(stamp)
        return True

    def on_shutdown(self, stamp):
        with self._lock:
            if self._state == 0:
                raise RuntimeError('monitor is already turned off')
            self.time_shutdown = stamp
            self._state = 0
            self.time_state = stamp
        return True

    def on_timer(self, stamp):
        return True

    def on_msg__a(self, msg, stamp):
        with self._lock:
            if self._state == MonitorState.ACTIVE:
                if (msg.x < 0):
                    self.witness.append(MsgRecord('/a', stamp, msg))
                    self._state = -2
                    self.time_state = stamp
                    self.on_violation(stamp, self.witness)
                    return True
        return False

    def _reset(self):
        self.witness = []
        self.time_launch = -1
        self.time_shutdown = -1
        self.time_state = -1


    def _noop(self, *args):
        pass


class Property1Monitor:
    __slots__ = (
        '_lock',          # concurrency control
        '_state',         # currently active state
        'witness',        # MsgRecord list of observed events
        'on_enter_scope', # callback upon entering the scope
        'on_exit_scope',  # callback upon exiting the scope
        'on_violation',   # callback upon verdict of False
        'on_success',     # callback upon verdict of True
        'time_launch',    # when was the monitor launched
        'time_shutdown',  # when was the monitor shutdown
        'time_state',     # when did the last state transition occur
        'cb_map',         # mapping of topic names to callback functions
    )

    PROP_ID = 'None'
    PROP_TITLE = '''None'''
    PROP_DESC = '''None'''
    HPL_PROPERTY = r'''globally: no /a { (x > 0) } within 0.1s'''

    def __init__(self):
        self._lock = Lock()
        self._reset()
        self.on_enter_scope = self._noop
        self.on_exit_scope = self._noop
        self.on_violation = self._noop
        self.on_success = self._noop
        self._state = 0
        self.cb_map = {
            '/a': self.on_msg__a,
        }

    @property
    def verdict(self):
        # with self._lock:
        s = self._state
        if s == -1:
            return True
        if s == -2:
            return False
        return None

    @property
    def is_online_state(self):
        # with self._lock:
        s = self._state
        return s != 0

    @property
    def is_inactive_state(self):
        # with self._lock:
        return self._state == 1

    @property
    def is_active_state(self):
        # with self._lock:
        return self._state == 2

    @property
    def is_safe_state(self):
        # with self._lock:
        return self._state == 3

    @property
    def is_falsifiable_state(self):
        # with self._lock:
        return self._state == 2

    def on_launch(self, stamp):
        with self._lock:
            if self._state != 0:
                raise RuntimeError('monitor is already turned on')
            self._reset()
            self.time_launch = stamp
            self._state = MonitorState.ACTIVE
            self.time_state = stamp
            self.on_enter_scope(stamp)
        return True

    def on_shutdown(self, stamp):
        with self._lock:
            if self._state == 0:
                raise RuntimeError('monitor is already turned off')
            self.time_shutdown = stamp
            self._state = 0
            self.time_state = stamp
        return True

    def on_timer(self, stamp):
        with self._lock:
            if self._state == 2 and (stamp - self.time_state) >= 0.1:
                self._state = -1
                self.time_state = stamp
                self.on_success(stamp, self.witness)
        return True

    def on_msg__a(self, msg, stamp):
        with self._lock:
            if self._state == 2 and (stamp - self.time_state) >= 0.1:
                self._state = -1
                self.time_state = stamp
                self.on_success(stamp, self.witness)
            if self._state == MonitorState.ACTIVE:
                if (msg.x > 0):
                    self.witness.append(MsgRecord('/a', stamp, msg))
                    self._state = -2
                    self.time_state = stamp
                    self.on_violation(stamp, self.witness)
                    return True
        return False

    def _reset(self):
        self.witness = []
        self.time_launch = -1
        self.time_shutdown = -1
        self.time_state = -1


    def _noop(self, *args):
        pass


###############################################################################
# Monitor Manager
###############################################################################


class HplMonitorManager:
    def __init__(self, success_cb=noop, failure_cb=noop):
        self.on_monitor_success = success_cb
        self.on_monitor_failure = failure_cb
        self.monitors = [
            Property0Monitor(),
            Property1Monitor(),
        ]
        n = len(self.monitors)
        for i in range(n):
            mon = self.monitors[i]
            mon.on_success = partial(self._on_success, i)
            mon.on_violation = partial(self._on_failure, i)
        self.live_server = LiveMonitoringServer()
        self.live_server.monitor_report = self.build_status_report()

    def start_live_server_thread(self):
        thread = Thread(target=self.live_server.run, name='live update server')
        thread.start()
        return thread

    def launch(self, timestamp):
        self.verdicts = []
        for mon in self.monitors:
            mon.on_launch(timestamp)

    def shutdown(self, timestamp):
        for mon in self.monitors:
            mon.on_shutdown(timestamp)
        self.live_server.request_shutdown()

    def on_timer(self, timestamp):
        for mon in self.monitors:
            mon.on_timer(timestamp)

    def on_msg__a(self, msg, timestamp):
        self.monitors[0].on_msg__a(msg, timestamp)
        self.monitors[1].on_msg__a(msg, timestamp)

    def _on_success(self, i, timestamp, witness):
        mon = self.monitors[i]
        assert mon.verdict is True
        self.live_server.on_monitor_success(i, timestamp, witness)
        self.on_monitor_success(mon, timestamp, witness)

    def _on_failure(self, i, timestamp, witness):
        mon = self.monitors[i]
        assert mon.verdict is False
        self.live_server.on_monitor_failure(i, timestamp, witness)
        self.on_monitor_failure(mon, timestamp, witness)

    def build_status_report(self):
        report = []
        for mon in self.monitors:
            report.append({
                'id': mon.PROP_ID,
                'title': mon.PROP_TITLE,
                'property': mon.HPL_PROPERTY,
                'verdict': mon.verdict,
            })
        return report


###############################################################################
# Live Monitoring
###############################################################################

# This is meant to be running on an async loop.
# You might want to run this on a separate thread,
# rather than the one used to run HplMonitorManager,
# if the message feed is built on a synchronous interface.

# Use `HplMonitorManager.build_status_report` to initialize
# the `monitor_report` attribute.


class LiveMonitoringServer:
    def __init__(self, host='127.0.0.1', port=4242):
        self.host = host
        self.port = port
        self.monitor_report = []
        self.shutdown_requested = asyncio.Event()
        self._lock = Lock()
        self._event_loop = None
        self._clients = []

    def request_shutdown(self):
        # to be called from outside the dedicated thread
        with self._lock:
            if self._event_loop is not None:
                coro = self._request_shutdown()
                asyncio.run_coroutine_threadsafe(coro, self._event_loop)

    async def _request_shutdown(self):
        await asyncio.sleep(0)
        self.shutdown_requested.set()

    def run(self):
        # to be called from the dedicated thread
        asyncio.run(self._run_server())

    async def _run_server(self):
        with self._lock:
            self._event_loop = asyncio.get_event_loop()
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        async with server:
            # await server.serve_forever()
            await self.shutdown_requested.wait()
        await self._push_update(None)  # poison pill
        with self._lock:
            self._event_loop = None

    async def _handle_client(self, reader, writer):
        client = LiveMonitoringClient(reader, writer)
        self._clients.append(client)
        with self._lock:
            report = deepcopy(self.monitor_report)
        if not self.shutdown_requested.is_set():
            await client.send_initial_report(report)
            await client.run_loop()

    def on_monitor_success(self, i, timestamp, witness):
        # to be called from outside the event loop
        v = Verdict(True, i, timestamp, witness)
        w = _witness_to_json(witness)
        with self._lock:
            self.monitor_report[i]['verdict'] = True
            self.monitor_report[i]['witness'] = w
            if self._event_loop is not None:
                coro = self._push_update(v)
                asyncio.run_coroutine_threadsafe(coro, self._event_loop)

    def on_monitor_failure(self, i, timestamp, witness):
        # to be called from outside the event loop
        v = Verdict(False, i, timestamp, witness)
        w = _witness_to_json(witness)
        with self._lock:
            self.monitor_report[i]['verdict'] = False
            self.monitor_report[i]['witness'] = w
            if self._event_loop is not None:
                coro = self._push_update(v)
                asyncio.run_coroutine_threadsafe(coro, self._event_loop)

    async def _push_update(self, verdict):
        for client in self.clients:
            await client.verdict_queue.put(verdict)


class LiveMonitoringClient:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.verdict_queue = asyncio.Queue()

    async def send_initial_report(self, report):
        data = json.dumps(report, separators=COMPACT) + '\n'
        writer.write(data.encode('utf8'))
        await writer.drain()

    async def run_loop(self):
        verdict = await self.verdict_queue.get()
        while verdict:
            data = _verdict_to_json(verdict)
            data = json.dumps(data, separators=COMPACT) + '\n'
            writer.write(data.encode('utf8'))
            await writer.drain()
            self.verdict_queue.task_done()
            verdict = await self.verdict_queue.get()
        self.verdict_queue.task_done()
        writer.close()