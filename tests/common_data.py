# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Final, Iterable, Optional

from attrs import frozen

from hplrv.monitors import EventType, MonitorState

###############################################################################
# Data Structures
###############################################################################


@frozen
class MsgRecord:
    topic: str
    timestamp: float
    msg: Any


@frozen
class ActivatorEvent:
    msg: Any
    state: MonitorState
    topic: str = 'p'

    @property
    def event(self) -> EventType:
        return EventType.ACTIVATOR


@frozen
class TerminatorEvent:
    msg: Any
    state: MonitorState
    topic: str = 'q'

    @property
    def event(self) -> EventType:
        return EventType.TERMINATOR


@frozen
class BehaviourEvent:
    msg: Any
    state: MonitorState
    topic: str = 'b'

    @property
    def event(self) -> EventType:
        return EventType.BEHAVIOUR


@frozen
class TriggerEvent:
    msg: Any
    state: MonitorState
    topic: str = 'a'

    @property
    def event(self) -> EventType:
        return EventType.TRIGGER


@frozen
class SpamEvent:
    topic: str
    msg: Any
    state: Optional[MonitorState] = None

    @property
    def event(self) -> EventType:
        return EventType.SPAM


@frozen
class TimerEvent:
    state: Optional[MonitorState] = None
    drops: int = 0

    @property
    def event(self) -> EventType:
        return EventType.TIMER


@frozen
class Point2D:
    x: float = 0
    y: float = 0


@frozen
class Array:
    xs: Iterable[int]


EMPTY_ARRAY: Final[Array] = Array(())
ARRAY_000: Final[Array] = Array((0, 0, 0))
ARRAY_010: Final[Array] = Array((0, 1, 0))
ARRAY_111: Final[Array] = Array((1, 1, 1))
ARRAY_123: Final[Array] = Array((1, 2, 3))
