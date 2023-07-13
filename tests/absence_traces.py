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

def globally_no():
    text = 'globally: no b {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# Global Scope With Timeout
###############################################################################

def globally_no_within():
    text = 'globally: no b {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2), state=MonitorState.TRUE),
    ])
    traces.append([
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.TRUE),
    ])
    traces.append([
        TimerEvent(),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1), state=MonitorState.TRUE),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# After Scope No Timeout
###############################################################################

def after_no():
    text = 'after p as P {x > 0}: no b {x > @P.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# After Scope With Timeout
###############################################################################

def after_no_within():
    text = 'after p as P {x > 0}: no b {x > @P.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.TRUE),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# Until Scope No Timeout
###############################################################################

def until_no():
    text = 'until q {x > 0}: no b {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# Until Scope With Timeout
###############################################################################

def until_no_within():
    text = 'until q {x > 0}: no b {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1), state=MonitorState.TRUE),
        SpamEvent('q', Point2D(x=1)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope No Timeout
###############################################################################

def after_until_no():
    text = 'after p as P {x + y > 0} until q {x > @P.x}: no b {x > @P.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=-2, y=3), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D()),
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D()),
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope With Timeout
###############################################################################

def after_until_no_within():
    text = 'after p as P {x + y > 0} until q {x > @P.x}: no b {x > @P.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=-2, y=3), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TimerEvent(state=MonitorState.SAFE),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D()),
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    return (text, traces)
