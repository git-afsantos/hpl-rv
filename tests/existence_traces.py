# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from hplrv.monitors import MonitorState

from .common_data import *

###############################################################################
# Global Scope No Timeout
###############################################################################

def globally_some():
    text = 'globally: some b {len(xs) > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([
        SpamEvent('b', EMPTY_ARRAY),
        TimerEvent(),
        SpamEvent('b', EMPTY_ARRAY),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        SpamEvent('b', ARRAY_123),
    ])
    # invalid
    # none, lol
    return (text, traces)

###############################################################################
# Global Scope With Timeout
###############################################################################

def globally_some_within():
    text = 'globally: some b {exists i in xs: xs[@i] > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ BehaviourEvent(ARRAY_010, MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', Array(())),
        BehaviourEvent(ARRAY_010, MonitorState.TRUE),
        TimerEvent(),
        SpamEvent('b', ARRAY_010),
    ])
    # invalid
    traces.append([
        SpamEvent('b', ARRAY_000),
        TimerEvent(),
        SpamEvent('b', ARRAY_010, state=MonitorState.FALSE),
    ])
    traces.append([
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.FALSE),
    ])
    return (text, traces)

###############################################################################
# After Scope No Timeout
###############################################################################

def after_some():
    text = 'after p as P {xs[1] > 0}: some b {xs[1] > @P.xs[1]}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', ARRAY_010) ])
    traces.append([ ActivatorEvent(ARRAY_010, MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', ARRAY_123),
        ActivatorEvent(ARRAY_010, MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', ARRAY_010),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        SpamEvent('b', ARRAY_123),
    ])
    # invalid
    # none, lol
    return (text, traces)

###############################################################################
# After Scope With Timeout
###############################################################################

def after_some_within():
    text = 'after p as P {xs[1] > 0}: some b {xs[1] > @P.xs[1]} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ ActivatorEvent(ARRAY_010, MonitorState.ACTIVE) ])
    traces.append([
        ActivatorEvent(ARRAY_010, MonitorState.ACTIVE),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE)
    ])
    traces.append([
        SpamEvent('b', ARRAY_010),
        TimerEvent(),
        ActivatorEvent(ARRAY_010, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_010),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        TimerEvent(),
        SpamEvent('b', ARRAY_123),
    ])
    # invalid
    traces.append([
        SpamEvent('b', ARRAY_010),
        ActivatorEvent(ARRAY_010, MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', ARRAY_010),
        SpamEvent('b', ARRAY_123, state=MonitorState.FALSE),
        SpamEvent('b', ARRAY_123),
    ])
    return (text, traces)

###############################################################################
# Until Scope No Timeout
###############################################################################

def until_some():
    text = 'until q {forall i in xs: xs[@i] = 0}: some b {sum(xs) > 3}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ SpamEvent('q', ARRAY_010) ])
    traces.append([ BehaviourEvent(ARRAY_123, MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', ARRAY_000),
        TimerEvent(),
        SpamEvent('q', ARRAY_010),
    ])
    traces.append([
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        SpamEvent('q', ARRAY_000),
    ])
    traces.append([
        SpamEvent('b', EMPTY_ARRAY),
        TimerEvent(),
        SpamEvent('b', ARRAY_111),
        SpamEvent('q', ARRAY_111),
        TimerEvent(),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        TimerEvent(),
        SpamEvent('b', ARRAY_123),
    ])
    # invalid
    traces.append([ TerminatorEvent(EMPTY_ARRAY, MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', ARRAY_111),
        SpamEvent('q', ARRAY_111),
        TimerEvent(),
        TerminatorEvent(ARRAY_000, MonitorState.FALSE),
        SpamEvent('b', ARRAY_123),
    ])
    return (text, traces)

###############################################################################
# Until Scope With Timeout
###############################################################################

def until_some_within():
    text = 'until q {forall i in xs: xs[@i] = 0}: some b {sum(xs) > 3} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ SpamEvent('q', ARRAY_010) ])
    traces.append([ BehaviourEvent(ARRAY_123, MonitorState.TRUE) ])
    traces.append([
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        SpamEvent('q', ARRAY_000),
    ])
    traces.append([
        SpamEvent('b', EMPTY_ARRAY),
        BehaviourEvent(ARRAY_123, MonitorState.TRUE),
        TimerEvent(),
        SpamEvent('b', ARRAY_111),
        SpamEvent('q', ARRAY_111),
        TimerEvent(),
        SpamEvent('b', ARRAY_123),
    ])
    # invalid
    traces.append([ TerminatorEvent(EMPTY_ARRAY, MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', ARRAY_000),
        TimerEvent(),
        SpamEvent('q', ARRAY_010, state=MonitorState.FALSE),
        SpamEvent('b', ARRAY_123),
    ])
    traces.append([
        TimerEvent(),
        TerminatorEvent(ARRAY_000, MonitorState.FALSE),
        SpamEvent('b', ARRAY_123),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope No Timeout
###############################################################################

def after_until_some():
    text = 'after p as P {prod(xs) = 1} until q {max(xs) < min(@P.xs)}: some b {prod(xs) >= prod(@P.xs)}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', ARRAY_010) ])
    traces.append([ SpamEvent('q', EMPTY_ARRAY) ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ ActivatorEvent(EMPTY_ARRAY, MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', EMPTY_ARRAY),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', ARRAY_010),
    ])
    traces.append([
        SpamEvent('p', ARRAY_010),
        SpamEvent('q', ARRAY_000),
        SpamEvent('b', ARRAY_111),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_000),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        SpamEvent('q', ARRAY_123),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
        SpamEvent('b', ARRAY_123),
        SpamEvent('q', ARRAY_000),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('q', ARRAY_010),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        SpamEvent('b', ARRAY_123),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        TerminatorEvent(ARRAY_000, MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('p', ARRAY_010),
        SpamEvent('q', ARRAY_000),
        SpamEvent('b', ARRAY_111),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_000),
        SpamEvent('q', ARRAY_123),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
        SpamEvent('b', ARRAY_123),
        SpamEvent('q', ARRAY_000),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_010),
        SpamEvent('q', ARRAY_010),
        TerminatorEvent(ARRAY_000, MonitorState.FALSE),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope With Timeout
###############################################################################

def after_until_some_within():
    text = 'after p as P {prod(xs) = 1} until q {max(xs) < min(@P.xs)}: some b {prod(xs) >= prod(@P.xs)} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', ARRAY_010) ])
    traces.append([ SpamEvent('q', EMPTY_ARRAY) ])
    traces.append([ SpamEvent('b', EMPTY_ARRAY) ])
    traces.append([ ActivatorEvent(EMPTY_ARRAY, MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', EMPTY_ARRAY),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', ARRAY_010),
    ])
    traces.append([
        SpamEvent('p', ARRAY_010),
        SpamEvent('q', ARRAY_000),
        SpamEvent('b', ARRAY_111),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_000),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        SpamEvent('q', ARRAY_123),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
        SpamEvent('b', ARRAY_123),
        SpamEvent('q', ARRAY_000),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('q', ARRAY_010),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        SpamEvent('b', ARRAY_123),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        TerminatorEvent(ARRAY_000, MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('p', ARRAY_010),
        SpamEvent('q', ARRAY_000),
        SpamEvent('b', ARRAY_111),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_000),
        BehaviourEvent(ARRAY_123, MonitorState.SAFE),
        SpamEvent('q', ARRAY_123),
        TerminatorEvent(ARRAY_000, MonitorState.INACTIVE),
        SpamEvent('b', ARRAY_123),
        SpamEvent('q', ARRAY_000),
        ActivatorEvent(ARRAY_111, MonitorState.ACTIVE),
        SpamEvent('b', ARRAY_010),
        SpamEvent('q', ARRAY_010),
        SpamEvent('b', ARRAY_123, state=MonitorState.FALSE),
        SpamEvent('q', ARRAY_000),
    ])
    return (text, traces)
