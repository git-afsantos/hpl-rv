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

def globally_forbids():
    text = 'globally: a {x > 0} forbids b {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=0)),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

def globally_forbids_ref():
    text = 'globally: a as A {x > 0} forbids b {x > 0 and x > @A.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=4)),
    ])
    return (text, traces)

###############################################################################
# Global Scope With Timeout
###############################################################################

def globally_forbids_within():
    text = 'globally: a {x > 0} forbids b {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D()) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=1)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D()),
        SpamEvent('b', Point2D()),
        SpamEvent('b', Point2D(x=1), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=1)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), None),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
    ])
    return (text, traces)

def globally_forbids_ref_within():
    text = 'globally: a as A {x > 0} forbids b {x > 0 and x > @A.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('a', Point2D()) ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=3)),
    ])
    return (text, traces)

###############################################################################
# After Scope No Timeout
###############################################################################

def after_forbids():
    text = 'after p as P {x > 0}: a {x > @P.x} forbids b {x > @P.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ SpamEvent('a', Point2D(x=1)) ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    # invalid
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('p', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=3)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    return (text, traces)

def after_forbids_ref():
    text = 'after p as P {x > 0}: a as A {x > @P.x} forbids b {x > @P.x and x > @A.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ SpamEvent('a', Point2D(x=1)) ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    # invalid
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('p', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=4)),
    ])
    return (text, traces)

###############################################################################
# After Scope With Timeout
###############################################################################

def after_forbids_within():
    text = 'after p as P {x > 0}: a {x > @P.x} forbids b {x > @P.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D(x=1)) ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TriggerEvent(Point2D(x=3), None),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    return (text, traces)

def after_forbids_ref_within():
    text = 'after p as P {x > 0}: a as A {x > @P.x} forbids b {x > @P.x and x > @A.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('p', Point2D()) ])
    traces.append([ SpamEvent('a', Point2D(x=1)) ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D()),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=3)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=3), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=4)),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        TimerEvent(),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        BehaviourEvent(Point2D(x=4), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=4)),
    ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=3)),
        BehaviourEvent(Point2D(x=4), MonitorState.FALSE),
    ])
    return (text, traces)

###############################################################################
# Until Scope No Timeout
###############################################################################

def until_forbids():
    text = 'until q {x > 0}: a {x > 0} forbids b {x > 0}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=0)),
        SpamEvent('a', Point2D(x=2)),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=0)),
        BehaviourEvent(Point2D(x=1), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
    ])
    return (text, traces)

def until_forbids_ref():
    text = 'until q {x > 0}: a as A {x > 0} forbids b {x > 0 and x > @A.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), None),
        SpamEvent('b', Point2D(x=1)),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=1), None),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    return (text, traces)

###############################################################################
# Until Scope With Timeout
###############################################################################

def until_forbids_within():
    text = 'until q {x > 0}: a {x > 0} forbids b {x > 0} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('a', Point2D()),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D()),
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
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D()),
        SpamEvent('b', Point2D()),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0), state=MonitorState.SAFE),
    ])
    # invalid
    traces.append([
        SpamEvent('b', Point2D()),
        TimerEvent(),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=2), None),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0)),
        SpamEvent('b', Point2D(x=0), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=0)),
        TriggerEvent(Point2D(x=1), None),
        SpamEvent('b', Point2D(x=0)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    return (text, traces)

def until_forbids_ref_within():
    text = 'until q {x > 0}: a as A {x > 0} forbids b {x > 0 and x > @A.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ TerminatorEvent(Point2D(x=1), MonitorState.TRUE) ])
    traces.append([ TriggerEvent(Point2D(x=1), MonitorState.ACTIVE) ])
    traces.append([
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('a', Point2D()),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D()),
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
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.TRUE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=1), None),
        SpamEvent('b', Point2D(x=1), None),
        SpamEvent('b', Point2D(x=1), None),
        SpamEvent('b', Point2D(x=3), state=MonitorState.SAFE),
        TerminatorEvent(Point2D(x=1), MonitorState.TRUE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.TRUE),
    ])
    # invalid
    traces.append([
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    traces.append([
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=1), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=1), None),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope No Timeout
###############################################################################

def after_until_forbids():
    text = 'after p as P {x > 0} until q {x > @P.x}: a {x > @P.x} forbids b {x > @P.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        SpamEvent('p', Point2D(x=3)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('a', Point2D(x=3)),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=2)),
    ])
    return (text, traces)

def after_until_forbids_ref():
    text = 'after p as P {x > 0} until q {x > @P.x}: a as A {x > @P.x} forbids b {x > @P.x and x > @A.x}'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        SpamEvent('p', Point2D(x=3)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('q', Point2D(x=2)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=3)),
        TriggerEvent(Point2D(x=2), None),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    return (text, traces)

###############################################################################
# After-Until Scope With Timeout
###############################################################################

def after_until_forbids_within():
    text = 'after p as P {x > 0} until q {x > @P.x}: a {x > @P.x} forbids b {x > @P.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=1)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        TimerEvent(),
        SpamEvent('b', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=1)),
        TimerEvent(),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=4), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('p', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=1)),
        BehaviourEvent(Point2D(x=2), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        SpamEvent('q', Point2D(x=2)),
    ])
    return (text, traces)

def after_until_forbids_ref_within():
    text = 'after p as P {x > 0} until q {x > @P.x}: a as A {x > @P.x} forbids b {x > @P.x and x > @A.x} within 3 s'
    traces = []
    # valid
    traces.append([])
    traces.append([ TimerEvent() ])
    traces.append([ SpamEvent('b', Point2D(x=1)) ])
    traces.append([ ActivatorEvent(Point2D(x=1), MonitorState.SAFE) ])
    traces.append([
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TimerEvent(),
        SpamEvent('a', Point2D(x=1)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=4), state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('b', Point2D(x=4), state=MonitorState.SAFE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        TerminatorEvent(Point2D(x=3), MonitorState.INACTIVE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=1)),
        SpamEvent('a', Point2D(x=1)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=3)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=3)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('b', Point2D(x=2)),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TriggerEvent(Point2D(x=3), None),
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
    ])
    # invalid
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        TimerEvent(),
        TimerEvent(state=MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TimerEvent(),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    traces.append([
        SpamEvent('p', Point2D()),
        SpamEvent('q', Point2D(x=2)),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        SpamEvent('a', Point2D(x=1)),
        SpamEvent('b', Point2D(x=1)),
        SpamEvent('q', Point2D(x=1)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=2)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=2), MonitorState.SAFE),
        TriggerEvent(Point2D(x=3), MonitorState.ACTIVE),
        BehaviourEvent(Point2D(x=4), MonitorState.FALSE),
        SpamEvent('b', Point2D(x=4)),
        SpamEvent('q', Point2D(x=4)),
    ])
    traces.append([
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=2), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=2)),
        TimerEvent(),
        SpamEvent('b', Point2D(x=2), state=MonitorState.SAFE),
        SpamEvent('b', Point2D(x=3)),
        TerminatorEvent(Point2D(x=2), MonitorState.INACTIVE),
        SpamEvent('a', Point2D(x=2)),
        SpamEvent('b', Point2D(x=3)),
        SpamEvent('q', Point2D(x=2)),
        ActivatorEvent(Point2D(x=1), MonitorState.SAFE),
        TriggerEvent(Point2D(x=4), MonitorState.ACTIVE),
        SpamEvent('b', Point2D(x=3)),
        TriggerEvent(Point2D(x=2), None),
        BehaviourEvent(Point2D(x=3), MonitorState.FALSE),
    ])
    return (text, traces)
