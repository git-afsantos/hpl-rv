# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

import asyncio
import importlib.util
from pathlib import Path
import sys
from threading import Thread

from hplrv.gen import lib_from_properties
from ..common_data import Point2D

###############################################################################
# Test Setup
###############################################################################

MODULE_NAME = 'generated_monitors'
FILE_NAME = f'{MODULE_NAME}.py'
FILE_PATH = Path(__file__).resolve(strict=True).parent / FILE_NAME
HOST = '127.0.0.1'
PORT = 4242


def example_properties():
    return [
        'globally: no /a {x < 0}',
        'globally: no /a {x > 0} within 100 ms',
    ]


def generate_monitors():
    code: str = lib_from_properties(example_properties())
    FILE_PATH.write_text(code, encoding='utf8')


def import_generated_monitors():
    spec = importlib.util.spec_from_file_location(MODULE_NAME, FILE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


###############################################################################
# Integration Test
###############################################################################


def test_live_monitoring_server():
    generate_monitors()
    lib = import_generated_monitors()
    man = lib.HplMonitorManager()
    man.live_server.host = HOST
    man.live_server.port = PORT
    thread: Thread = man.live_server.start_thread()
    asyncio.run(integration_task(man, thread))


async def integration_task(man, thread: Thread):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    report = await reader.readline()
    assert report.decode('utf8').startswith('[')
    man.launch(0.0)
    man.on_timer(0.2)
    assert man.monitors[1].verdict is True
    report = await reader.readline()
    assert report.decode('utf8').startswith('{')
    man.on_msg__a(Point2D(x=-1), 0.5)
    assert man.monitors[0].verdict is False
    report = await reader.readline()
    assert report.decode('utf8').startswith('{')
    man.shutdown(1.0)
    thread.join(10.0)
    assert not thread.is_alive()
