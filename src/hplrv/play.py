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
import pkg_resources
import sys
from threading import Thread

from hplrv.traces import Trace

###############################################################################
# Constants
###############################################################################

PROG_PLAY: Final[str] = 'hpl-rv play'

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


###############################################################################
# Public Interface
###############################################################################


async def trace_replay(man, thread: Thread, trace: Optional[Trace]):
    # reader, writer = await asyncio.open_connection(man.live_server.host, man.live_server.port)
    # report = await reader.readline()
    # assert report.decode('utf8').startswith('[')
    man.launch(0.0)
    man.on_timer(0.2)
    # assert man.monitors[1].verdict is True
    # report = await reader.readline()
    # assert report.decode('utf8').startswith('{')
    man.on_msg__a((1, 1))
    # assert man.monitors[0].verdict is False
    # report = await reader.readline()
    # assert report.decode('utf8').startswith('{')
    man.shutdown(1.0)
    thread.join(10.0)
    assert not thread.is_alive()


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
    trace: Optional[Trace] = None
    file_path = args.get('data')
    if file_path is not None:
        trace = import_trace_from_json_file(file_path)
    man = lib.HplMonitorManager()
    man.live_server.host = args['host']
    man.live_server.port = args['port']
    thread: Thread = man.live_server.start_thread()
    asyncio.run(trace_replay(man, thread, trace))
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

    args = parser.parse_args(args=argv)
    return vars(args)
