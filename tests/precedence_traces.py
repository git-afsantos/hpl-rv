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

def globally_requires():
    text = 'globally: b {x > 0} requires a {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('a', Point2D(x=-2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

def globally_requires_ref():
    text = 'globally: b as B {x > 0} requires a {x > 0 and x > @B.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TriggerEvent(Point2D(x=1), None) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('a', Point2D(x=-2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        TriggerEvent(Point2D(x=1), None),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# Global Scope With Timeout
###############################################################################

def globally_requires_within():
    text = 'globally: b {x > 0} requires a {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(state=MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(state=MonitorState.ACTIVE),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(state=MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

def globally_requires_ref_within():
    text = 'globally: b as B {x > 0} requires a {x > 0 and x > @B.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), None),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TriggerEvent(Point2D(x=2), None),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([ BehaviourEvent(Point2D(x=1), MonitorState.FALSE) ])
    traces.append([
        SpamEvent('b', Point2D()),
        TriggerEvent(Point2D(x=1), None),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), None),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# After Scope No Timeout
###############################################################################

def after_requires():
    text = 'after p as P {x > 0}: b {x > @P.x} requires a {x > @P.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('p', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.TRUE),
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
        SpamEvent('a', Point2D(x=2)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

def after_requires_ref():
    text = 'after p as P {x > 0}: b as B {x > @P.x} requires a {x > @P.x and x > @B.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('p', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), None),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

###############################################################################
# After Scope With Timeout
###############################################################################

def after_requires_within():
    text = 'after p as P {x > 0}: b {x > @P.x} requires a {x > @P.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(state=MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TimerEvent(),
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
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

def after_requires_ref_within():
    text = 'after p as P {x > 0}: b as B {x > @P.x} requires a {x > @P.x and x > @B.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=3), None),
        TimerEvent(),
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
        TriggerEvent(Point2D(x=3), None),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

###############################################################################
# Until Scope No Timeout
###############################################################################

def until_requires():
    text = 'until q {x > 0}: b {x > 0} requires a {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
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
        SpamEvent('a', Point2D()),
        SpamEvent('q', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    return (text, traces)

def until_requires_ref():
    text = 'until q {x > 0}: b as B {x > 0} requires a {x > 0 and x > @B.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), None) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        SpamEvent('a', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=1), None),
        SpamEvent('b', Point2D()),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=3)),
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
        TriggerEvent(Point2D(x=1), None),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    return (text, traces)

###############################################################################
# Until Scope With Timeout
###############################################################################

def until_requires_within():
    text = 'until q {x > 0}: b {x > 0} requires a {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(state=MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
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
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D()),
        SpamEvent('q', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
    ])
    return (text, traces)

def until_requires_ref_within():
    text = 'until q {x > 0}: b as B {x > 0} requires a {x > 0 and x > @B.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), None) ])
    traces.append([
        SpamEvent('b', Point2D(x=-1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=-2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), None),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), None),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
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
        TriggerEvent(Point2D(x=1), None),
        SpamEvent('a', Point2D()),
        SpamEvent('q', Point2D()),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), None),
        TriggerEvent(Point2D(x=1), None),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), None),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope No Timeout
###############################################################################

def after_until_requires():
    text = 'after p as P {x > 0} until q {x > @P.x}: b {x > @P.x} requires a {x > @P.x}'
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
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
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
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D()),
        SpamEvent('a', Point2D()),
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    return (text, traces)

def after_until_requires_ref():
    text = 'after p as P {x > 0} until q {x > @P.x}: b as B {x > @P.x} requires a {x > @P.x and x > @B.x}'
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
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
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
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D()),
        SpamEvent('a', Point2D()),
        SpamEvent('b', Point2D()),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        TriggerEvent(Point2D(x=4), None),
        BehaviourEvent(Point2D(x=4), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope With Timeout
###############################################################################

def after_until_requires_within():
    text = 'after p as P {x > 0} until q {x > @P.x}: b {x > @P.x} requires a {x > @P.x} within 3 s'
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
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=1), state=MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        TimerEvent(state=MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        TimerEvent(state=MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=4), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    return (text, traces)

def after_until_requires_ref_within():
    text = 'after p as P {x > 0} until q {x > @P.x}: b as B {x > @P.x} requires a {x > @P.x and x > @B.x} within 3 s'
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
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=4), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=4), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE)
    ])
    traces.append([
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=4), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=4), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=4), None),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
    ])
    return (text, traces)
