# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'replay' command line program and a utility
to replay traces of messages to test monitors.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional

import argparse
import asyncio
import importlib.util
import json
from pathlib import Path
from random import shuffle
import sys
from threading import Thread
from time import sleep

from hplrv.traces import Trace

###############################################################################
# Constants
###############################################################################

PROG_PLAY: Final[str] = 'hpl-rv play'


def noop(*args, **kwargs):
    pass


###############################################################################
# Setup Functions
###############################################################################


def import_generated_monitors(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def import_trace_from_json_file(file_path: Path) -> Trace:
    text: str = file_path.read_text(encoding='utf8')
    data: List[Dict[str, Any]] = json.loads(text)
    return Trace.from_list_of_dict(data)


def print_monitor_success(monitor, timestamp, witness):
    print(f'> Success @{timestamp}s')
    print(f'  [HPL]: {monitor.HPL_PROPERTY}')
    print(f'  [witness]: {witness}')


def print_monitor_failure(monitor, timestamp, witness):
    print(f'> Failure @{timestamp}s')
    print(f'  [HPL]: {monitor.HPL_PROPERTY}')
    print(f'  [witness]: {witness}')


###############################################################################
# Public Interface
###############################################################################


def trace_replay(monitor, trace: Trace, freq: float, shutdown: bool = True) -> float:
    now: float = 0.0
    next: float = freq
    monitor.launch(now)

    for event in trace.events:
        t = event.timestamp

        # wait until the next timestamp with messages
        while next < t:
            sleep(next - now)
            now = next
            next += freq
            monitor.on_timer(now)
        assert next >= t, f'{next} < {t}'
        if next > t:
            # wait the remaining time until message event
            sleep(t - now)
        else:
            next += freq
        now = t

        # dispatch simultaneous messages in a random order
        msgs = list(event.messages)
        shuffle(msgs)
        for msg in msgs:
            topic = msg.topic.replace('/', '_')
            cb = getattr(monitor, f'on_msg_{topic}', noop)
            cb(msg.data, now)

    # wait until the next timer event
    sleep(next - now)
    monitor.on_timer(now)
    # end of trace
    if shutdown:
        monitor.shutdown(now)
    return now


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
    file_path: Optional[Path] = args['module'].resolve(strict=True)
    lib = import_generated_monitors(file_path.stem, file_path)
    file_path = args.get('data')
    if file_path is None:
        return 0
    trace: Trace = import_trace_from_json_file(file_path)
    freq: float = args.get('frequency', 1.0)
    man = lib.HplMonitorManager()
    man.on_monitor_success = print_monitor_success
    man.on_monitor_failure = print_monitor_failure
    man.live_server.host = args['host']
    man.live_server.port = args['port']
    thread: Thread = man.live_server.start_thread()
    timestamp = trace_replay(man, trace, freq, shutdown=False)
    print('End of trace.')
    print('Press Ctrl+C to exit.')
    try:
        while True:
            sleep(1.0)
    except KeyboardInterrupt:
        pass
    man.shutdown(timestamp)
    thread.join(10.0)
    return 0


###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    description = 'Utility to run monitors and replay traces.'
    parser = argparse.ArgumentParser(prog=PROG_PLAY, description=description)

    parser.add_argument(
        'module',
        type=Path,
        help='path to a module with generated monitors'
    )

    parser.add_argument(
        '-d',
        '--data',
        type=Path,
        help=f'path to a data file containing a message trace',
    )

    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='address of the live monitoring server (default: 127.0.0.1)'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=4242,
        help=f'port of the live monitoring server (default: 4242)',
    )

    parser.add_argument(
        '-f',
        '--frequency',
        type=float,
        default=1.0,
        help=f'timestamp increment between trace events (default: 1)',
    )

    args = parser.parse_args(args=argv)
    return vars(args)
