# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from typing import Any, Iterable, List, Mapping, Optional, Tuple

from bisect import bisect, bisect_left
from types import SimpleNamespace

from attrs import field, frozen

###############################################################################
# Data Structures
###############################################################################


@frozen
class Message:
    topic: str
    data: Any = field(order=False)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> 'Message':
        return cls(data['topic'], SimpleNamespace(**data.get('data', {})))


@frozen(order=True)
class TraceEvent:
    timestamp: float
    messages: Tuple[Message] = field(factory=tuple, order=False, converter=tuple)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> 'TraceEvent':
        messages = map(Message.from_dict, data.get('messages', []))
        return cls(data['timestamp'], messages)

    def merge(self, other: 'TraceEvent') -> 'TraceEvent':
        if self.timestamp != other.timestamp:
            raise ValueError(f'timestamps differ: {self.timestamp} != {other.timestamp}')
        messages = self.messages + other.messages
        return TraceEvent(self.timestamp, messages)


@frozen
class Trace:
    events: Tuple[TraceEvent] = field(factory=tuple, converter=tuple)

    @events.validator
    def _ensure_sorted_timestamps(self, _attr: Any, events: Iterable[TraceEvent]) -> None:
        if not is_sorted(events):
            raise ValueError(f'unsorted events: {events}')

    @classmethod
    def from_unsorted_events(cls, unsorted_events: Iterable[TraceEvent]) -> 'Trace':
        # ensure that all duplicate timestamps are merged
        events = []
        for event in unsorted_events:
            insort_event(events, event)
        return cls(events)

    @classmethod
    def from_list_of_dict(cls, data: Iterable[Mapping[str, Any]]) -> 'Trace':
        events = map(TraceEvent.from_dict, data)
        return Trace(events)

    def add(self, event: TraceEvent) -> 'Trace':
        events = list(self.events)
        insort_event(events, event)
        return Trace(events)

    def merge(self, other: 'Trace') -> 'Trace':
        events = list(self.events)
        for event in other.events:
            insort_event(events, event)
        return Trace(events)

    def previous_timestamp(self, timestamp: float) -> Optional[float]:
        # returns the timestamp of the first event
        # that comes before (<) the given timestamp, or None
        i = bisect_left(self.events, timestamp, key=get_timestamp)
        return None if i <= 0 else self.events[i-1].timestamp

    def next_timestamp(self, timestamp: float) -> Optional[float]:
        # returns the timestamp of the first event
        # that comes after (>) the given timestamp, or None
        i = bisect(self.events, timestamp, key=get_timestamp)
        return None if i >= len(self.events) else self.events[i].timestamp


###############################################################################
# Helper Functions
###############################################################################


def is_sorted(items: Iterable[Any]) -> bool:
    return all(items[i] <= items[i+1] for i in range(len(items) - 1))


def insort_event(events: List[TraceEvent], event: TraceEvent) -> None:
    i = bisect(events, event)
    if i > 0 and events[i-1].timestamp == event.timestamp:
        events[i-1] = events[i-1].merge(event)
    else:
        events.insert(i, event)


def get_timestamp(event: TraceEvent) -> float:
    return event.timestamp
