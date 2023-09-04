# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from collections import deque       # needed by PropertyMonitor
from threading import Lock          # needed by PropertyMonitor

from hpl.parser import property_parser

from hplrv.gen import MonitorGenerator
from hplrv.monitors import EventType, MonitorState

from .common_data import *
from .absence_traces import *
from .existence_traces import *
from .precedence_traces import *
from .response_traces import *
from .prevention_traces import *

###############################################################################
# Test Case Generation
###############################################################################

def absence_properties():
    yield globally_no()
    yield globally_no_within()
    yield after_no()
    yield after_no_within()
    yield until_no()
    yield until_no_within()
    yield after_until_no()
    yield after_until_no_within()

def existence_properties():
    yield globally_some()
    yield globally_some_within()
    yield after_some()
    yield after_some_within()
    yield until_some()
    yield until_some_within()
    yield after_until_some()
    yield after_until_some_within()

def precedence_properties():
    yield globally_requires()
    yield globally_requires_ref()
    yield globally_requires_within()
    yield globally_requires_ref_within()
    yield after_requires()
    yield after_requires_ref()
    yield after_requires_within()
    yield after_requires_ref_within()
    yield until_requires()
    yield until_requires_ref()
    yield until_requires_within()
    yield until_requires_ref_within()
    yield after_until_requires()
    yield after_until_requires_ref()
    yield after_until_requires_within()
    yield after_until_requires_ref_within()

def response_properties():
    yield globally_causes()
    yield globally_causes_ref()
    yield globally_causes_within()
    yield globally_causes_ref_within()
    yield after_causes()
    yield after_causes_ref_within()
    yield until_causes()
    yield until_causes_ref()
    yield until_causes_within()
    yield until_causes_ref_within()
    yield after_until_causes()
    yield after_until_causes_ref()
    yield after_until_causes_within()
    yield after_until_causes_ref_within()

def prevention_properties():
    yield globally_forbids()
    yield globally_forbids_ref()
    yield globally_forbids_within()
    yield globally_forbids_ref_within()
    yield after_forbids()
    yield after_forbids_ref()
    yield after_forbids_within()
    yield after_forbids_ref_within()
    yield until_forbids()
    yield until_forbids_ref()
    yield until_forbids_within()
    yield until_forbids_ref_within()
    yield after_until_forbids()
    yield after_until_forbids_ref()
    yield after_until_forbids_within()
    yield after_until_forbids_ref_within()

def all_types_of_property():
    # example = text, traces
    for example in absence_properties():
        yield example
    for example in existence_properties():
        yield example
    for example in precedence_properties():
        yield example
    for example in response_properties():
        yield example
    for example in prevention_properties():
        yield example


###############################################################################
# Test Loop
###############################################################################


def state_name(s: MonitorState):
    if s is None:
        return '(none)'
    try:
        return s.name
    except AttributeError:
        return 'STATE {}'.format(s)


def pretty_trace(trace):
    s = []
    t = 0
    for e in trace:
        t += 1
        etype = e.event
        if etype == EventType.TIMER:
            s.append('@ {}: (Timer, -{}) -> {}'.format(
                t, e.drops, state_name(e.state)))
        elif etype == EventType.ACTIVATOR:
            s.append("@ {}: (Activator) '{}' {} -> {}".format(
                t, e.topic, e.msg, state_name(e.state)))
        elif etype == EventType.TERMINATOR:
            s.append("@ {}: (Terminator) '{}' {} -> {}".format(
                t, e.topic, e.msg, state_name(e.state)))
        elif etype == EventType.BEHAVIOUR:
            s.append("@ {}: (Behaviour) '{}' {} -> {}".format(
                t, e.topic, e.msg, state_name(e.state)))
        elif etype == EventType.TRIGGER:
            s.append("@ {}: (Trigger) '{}' {} -> {}".format(
                t, e.topic, e.msg, state_name(e.state)))
        else:
            s.append("@ {}: (Spam) '{}' {}".format(
                t, e.topic, e.msg))
    return "\n".join(s)

def pretty_monitor(m):
    return "\n".join((
        'm._state = {}'.format(m._state),
        'm.time_launch = {}'.format(m.time_launch),
        'm.time_shutdown = {}'.format(m.time_shutdown),
        'm.time_state = {}'.format(m.time_state),
        'm.witness = {}'.format(m.witness),
        'm._pool = {}'.format(getattr(m, '_pool', None)),
    ))


def prod(iterable):
    x = 1
    for y in iterable:
        x = x * y
        if x == 0:
            return 0
    return x


class TestMonitorClasses:
    def test_examples(self):
        self._reset()
        n = 0
        p = property_parser()
        r = MonitorGenerator(lang='py')
        for text, traces in all_types_of_property():
            hp = p.parse(text)
            self.pool_decay = ((hp.pattern.is_requirement
                    or hp.pattern.is_response
                    or hp.pattern.is_prevention)
                and hp.pattern.has_max_time)
            py = r.monitor_class(hp)
            m = self._make_monitor(py)
            for trace in traces:
                n += 1
                self.hpl_string = text
                self._set_trace_string(trace, n)
                self._launch(hp, m)
                time = 0
                for event in trace:
                    time += 1
                    self._dispatch(m, event, time)
                self._shutdown(m)
                self._reset()
        print('Tested {} examples.'.format(n))

    def _reset(self):
        self.debug_string = ''
        self.trace_string = ''
        self.hpl_string = ''
        self.entered_scope = []
        self.exited_scope = []
        self.found_success = []
        self.found_failure = []

    def _make_monitor(self, py):
        loc = dict(locals())
        exec(py, globals(), loc)
        cls = loc['PropertyMonitor']
        m = cls()
        m.on_enter_scope = self._on_enter
        m.on_exit_scope = self._on_exit
        m.on_success = self._on_success
        m.on_violation = self._on_failure
        self._update_debug_string(m, -1)
        assert m._state == MonitorState.OFF, self.debug_string
        assert m.verdict is None, self.debug_string
        assert not m.witness, self.debug_string
        assert m.time_launch < 0, self.debug_string
        assert m.time_state < 0, self.debug_string
        assert m.time_shutdown < 0, self.debug_string
        return m

    def _launch(self, hp, m):
        m.on_launch(0)
        self._update_debug_string(m, 0)
        if hp.scope.is_global or (hp.scope.is_until and not hp.scope.is_after):
            assert len(self.entered_scope) == 1, self.debug_string
            assert self.entered_scope[0] == 0, self.debug_string
        else:
            assert not self.entered_scope, self.debug_string
        assert not self.exited_scope, self.debug_string
        assert not self.found_success, self.debug_string
        assert not self.found_failure, self.debug_string
        assert m._state != MonitorState.OFF, self.debug_string
        assert m.verdict is None, self.debug_string
        assert not m.witness, self.debug_string
        assert m.time_launch == 0, self.debug_string
        assert m.time_state == 0, self.debug_string
        assert m.time_shutdown < 0, self.debug_string
        try:
            m.on_launch(0)
            self._update_debug_string(m, 0)
            assert False, self.debug_string
        except RuntimeError:
            pass # expected

    def _dispatch(self, m, event, time):
        etype = event.event
        if etype == EventType.TIMER:
            self._dispatch_timer(m, event, time)
        elif etype == EventType.ACTIVATOR:
            self._dispatch_activator(m, event, time)
        elif etype == EventType.TERMINATOR:
            self._dispatch_terminator(m, event, time)
        elif etype == EventType.BEHAVIOUR:
            self._dispatch_behaviour(m, event, time)
        elif etype == EventType.TRIGGER:
            self._dispatch_trigger(m, event, time)
        else:
            self._dispatch_spam(m, event, time)

    def _dispatch_activator(self, m, event, time):
        n = len(self.entered_scope)
        assert m._state == MonitorState.INACTIVE, self.debug_string
        consumed = self._dispatch_msg(m, event.topic, event.msg, time)
        self._update_debug_string(m, time)
        assert consumed, self.debug_string
        assert len(self.entered_scope) == n + 1, self.debug_string
        assert self.entered_scope[-1] == time, self.debug_string
        assert len(self.exited_scope) == n, self.debug_string
        assert not self.found_success, self.debug_string
        assert not self.found_failure, self.debug_string
        assert m._state == event.state, self.debug_string
        assert m.verdict is None, self.debug_string
        assert len(m.witness) == 1, self.debug_string
        assert m.witness[-1].topic == event.topic, self.debug_string
        assert m.witness[-1].timestamp == time, self.debug_string
        assert m.witness[-1].msg == event.msg, self.debug_string
        assert m.time_state == time, self.debug_string

    def _dispatch_terminator(self, m, event, time):
        n = len(self.exited_scope)
        assert m._state > MonitorState.INACTIVE, self.debug_string
        consumed = self._dispatch_msg(m, event.topic, event.msg, time)
        self._update_debug_string(m, time)
        assert consumed, self.debug_string
        assert len(self.exited_scope) == n + 1, self.debug_string
        assert self.exited_scope[-1] == time, self.debug_string
        assert len(self.entered_scope) == n + 1, self.debug_string
        self._check_verdict(m, event, time)
        if event.state == MonitorState.INACTIVE:
            assert not m.witness, self.debug_string
            assert not getattr(m, '_pool', None), self.debug_string

    def _dispatch_behaviour(self, m, event, time):
        a = len(self.entered_scope)
        b = len(self.exited_scope)
        s = m._state
        assert m._state == MonitorState.ACTIVE or m._state == MonitorState.SAFE, \
               self.debug_string
        consumed = self._dispatch_msg(m, event.topic, event.msg, time)
        self._update_debug_string(m, time)
        assert consumed, self.debug_string
        assert len(self.entered_scope) == a, self.debug_string
        assert len(self.exited_scope) == b, self.debug_string
        if event.state is None:
            assert m._state == s, self.debug_string
        self._check_verdict(m, event, time)

    def _dispatch_trigger(self, m, event, time):
        a = len(self.entered_scope)
        b = len(self.exited_scope)
        k = -1 if not hasattr(m, '_pool') else len(m._pool)
        s = m._state
        consumed = self._dispatch_msg(m, event.topic, event.msg, time)
        self._update_debug_string(m, time)
        assert consumed, self.debug_string
        assert len(self.entered_scope) == a, self.debug_string
        assert len(self.exited_scope) == b, self.debug_string
        if event.state is None:
            assert m._state == s, self.debug_string
        self._check_verdict(m, event, time)
        if k >= 0:
            assert len(m._pool) >= k, self.debug_string
            assert m._pool[-1].topic == event.topic, self.debug_string
            assert m._pool[-1].timestamp == time, self.debug_string
            assert m._pool[-1].msg == event.msg, self.debug_string

    def _dispatch_spam(self, m, event, time):
        a = len(self.entered_scope)
        b = len(self.exited_scope)
        k = len(getattr(m, '_pool', ()))
        n = len(m.witness)
        s = m._state
        t = m.time_state
        consumed = self._dispatch_msg(m, event.topic, event.msg, time)
        self._update_debug_string(m, time)
        assert not consumed, self.debug_string
        assert len(self.entered_scope) == a, self.debug_string
        assert len(self.exited_scope) == b, self.debug_string
        if self.pool_decay:
            assert len(getattr(m, '_pool', ())) <= k, self.debug_string
        else:
            assert len(getattr(m, '_pool', ())) == k, self.debug_string
        self._check_automatic_transition(m, event.state, time, s, t)

    def _dispatch_msg(self, m, topic, msg, time):
        cb = getattr(m, 'on_msg_' + topic)
        return cb(msg, time)

    def _dispatch_timer(self, m, event, time):
        a = len(self.entered_scope)
        b = len(self.exited_scope)
        k = len(getattr(m, '_pool', ()))
        s = m._state
        t = m.time_state
        m.on_timer(time)
        self._update_debug_string(m, time)
        assert len(self.entered_scope) == a, self.debug_string
        assert len(self.exited_scope) == b, self.debug_string
        assert len(getattr(m, '_pool', ())) <= k, self.debug_string
        self._check_automatic_transition(m, event.state, time, s, t)

    def _shutdown(self, m):
        m.on_shutdown(1000)
        self._update_debug_string(m, 1000)
        assert m._state == MonitorState.OFF, self.debug_string
        assert m.time_launch == 0, self.debug_string
        assert m.time_state >= 0, self.debug_string
        assert m.time_shutdown == 1000, self.debug_string
        try:
            m.on_shutdown(2000)
            self._update_debug_string(m, 2000)
            assert False, self.debug_string
        except RuntimeError:
            pass # expected

    def _check_verdict(self, m, event, time):
        if event.state is not None:
            assert m._state == event.state, self.debug_string
        if event.state == MonitorState.TRUE:
            assert len(self.found_success) == 1, self.debug_string
            assert self.found_success[0][0] == time, self.debug_string
            assert self.found_success[0][1] == m.witness, self.debug_string
            assert m.verdict is True, self.debug_string
            assert len(m.witness) >= 1, self.debug_string
            assert m.witness[-1].topic == event.topic, self.debug_string
            assert m.witness[-1].timestamp == time, self.debug_string
            assert m.witness[-1].msg == event.msg, self.debug_string
            assert m.time_state == time, self.debug_string
        elif event.state == MonitorState.FALSE:
            assert len(self.found_failure) == 1, self.debug_string
            assert self.found_failure[0][0] == time, self.debug_string
            assert self.found_failure[0][1] == m.witness, self.debug_string
            assert m.verdict is False, self.debug_string
            assert len(m.witness) >= 1, self.debug_string
            assert m.witness[-1].topic == event.topic, self.debug_string
            assert m.witness[-1].timestamp == time, self.debug_string
            assert m.witness[-1].msg == event.msg, self.debug_string
            assert m.time_state == time, self.debug_string
        else:
            assert not self.found_success, self.debug_string
            assert not self.found_failure, self.debug_string
            assert m.verdict is None, self.debug_string

    def _check_automatic_transition(self, m, s2, t2, s1, t1):
        if s2 == MonitorState.TRUE:
            assert len(self.found_success) == 1, self.debug_string
            assert self.found_success[0][0] == t2, self.debug_string
            assert self.found_success[0][1] == m.witness, self.debug_string
            assert m.verdict is True, self.debug_string
            assert m.time_state == t2, self.debug_string
            assert m._state == s2, self.debug_string
        elif s2 == MonitorState.FALSE:
            assert len(self.found_failure) == 1, self.debug_string
            assert self.found_failure[0][0] == t2, self.debug_string
            assert self.found_failure[0][1] == m.witness, self.debug_string
            assert m.verdict is False, self.debug_string
            assert m.time_state == t2, self.debug_string
            assert m._state == s2, self.debug_string
        elif s2 is not None:
            assert not self.found_success, self.debug_string
            assert not self.found_failure, self.debug_string
            assert m.verdict is None, self.debug_string
            assert m._state == s2, self.debug_string
        else:
            assert m._state == s1, self.debug_string
            assert m.time_state == t1, self.debug_string

    def _on_enter(self, stamp):
        self.entered_scope.append(stamp)

    def _on_exit(self, stamp):
        self.exited_scope.append(stamp)

    def _on_success(self, stamp, witness):
        self.found_success.append((stamp, witness))

    def _on_failure(self, stamp, witness):
        self.found_failure.append((stamp, witness))

    def _set_trace_string(self, trace, n):
        self.trace_string = f'[Example #{n}]:\n{pretty_trace(trace)}'

    def _update_debug_string(self, m, time):
        self.debug_string = (
            'failed for the following test'
            f'\n  [HPL]: {self.hpl_string}'
            f'\n  {self.trace_string}'
            f'\n  [Timestamp]: {time}'
            '\n  [Monitor]:'
            f'\n{pretty_monitor(m)}'
        )
