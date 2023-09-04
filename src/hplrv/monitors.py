# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from typing import Optional

from collections import defaultdict
from enum import IntEnum

from attrs import frozen
from hpl.ast import HplPredicate, HplVacuousTruth
from hpl.rewrite import refactor_reference, replace_this_with_var, replace_var_with_this

###############################################################################
# Constants
###############################################################################

INF = float('inf')


class MonitorState(IntEnum):
    OFF = 0
    TRUE = -1
    FALSE = -2
    INACTIVE = 1
    ACTIVE = 2
    SAFE = 3


class EventType(IntEnum):
    TIMER = 0
    ACTIVATOR = 1
    TERMINATOR = 2
    BEHAVIOUR = 3
    TRIGGER = 4
    SPAM = 5


###############################################################################
# Data Structures
###############################################################################


@frozen
class MonitoringEvent:
    predicate: HplPredicate

    @property
    def event_type(self) -> int:
        raise NotImplementedError()


@frozen
class ActivatorEvent(MonitoringEvent):
    @property
    def event_type(self) -> int:
        return EventType.ACTIVATOR


@frozen
class TerminatorEvent(MonitoringEvent):
    activator: Optional[str] = None
    verdict: Optional[bool] = None

    @property
    def event_type(self) -> int:
        return EventType.TERMINATOR


@frozen
class BehaviourEvent(MonitoringEvent):
    activator: Optional[str] = None
    trigger: Optional[str] = None

    @property
    def event_type(self) -> int:
        return EventType.BEHAVIOUR


@frozen
class TriggerEvent(MonitoringEvent):
    activator: Optional[str] = None

    @property
    def event_type(self) -> int:
        return EventType.TRIGGER


def _default_dict_of_lists():
    return defaultdict(list)


###############################################################################
# State Machine Builder
###############################################################################


class PatternBasedBuilder:
    # initial_state: int
    # timeout: float
    # reentrant_scope: bool
    # pool_size: -1|0|int
    # on_msg:
    #    <topic>:
    #        <state>:
    #            - <event>

    def __init__(self, hpl_property, s0):
        self.property_id = hpl_property.metadata.get('id')
        self.property_title = hpl_property.metadata.get('title')
        self.property_desc = hpl_property.metadata.get('description')
        self.property_text = str(hpl_property)
        self.class_name = 'PropertyMonitor'
        self._activator = None
        self._trigger = None
        self.reentrant_scope = False
        self.timeout = hpl_property.pattern.max_time
        if self.timeout == INF:
            self.timeout = -1
        event = hpl_property.scope.activator
        self.launch_enters_scope = event is None
        if event is not None and event.is_simple_event:
            self._activator = event.alias
        event = hpl_property.pattern.trigger
        if event is not None and event.is_simple_event:
            self._trigger = event.alias
        self.pool_size = self.calc_pool_size(hpl_property)
        self.on_msg = defaultdict(_default_dict_of_lists)
        if hpl_property.scope.is_global:
            self.initial_state = s0
        elif hpl_property.scope.is_after and hpl_property.scope.is_until:
            self.initial_state = MonitorState.INACTIVE
            self.reentrant_scope = True
            self.add_activator(hpl_property.scope.activator)
            self.add_terminator(hpl_property.scope.terminator)
        elif hpl_property.scope.is_after:
            self.initial_state = MonitorState.INACTIVE
            self.add_activator(hpl_property.scope.activator)
        elif hpl_property.scope.is_until:
            self.initial_state = s0
            self.add_terminator(hpl_property.scope.terminator)
        else:
            raise ValueError('unknown scope: ' + str(hpl_property.scope))
        self.add_behaviour(hpl_property.pattern.behaviour)
        if hpl_property.pattern.trigger is not None:
            self.add_trigger(hpl_property.pattern.trigger)

    def add_activator(self, event):
        # must be called before all others
        # assuming only disjunctions or simple events
        for e in event.simple_events():
            datum = ActivatorEvent(e.predicate)
            self.on_msg[e.name][MonitorState.INACTIVE].append(datum)

    def add_terminator(self, event):
        raise NotImplementedError()

    def add_trigger(self, event):
        raise NotImplementedError()

    def add_behaviour(self, event):
        raise NotImplementedError()

    def calc_pool_size(self, hpl_property):
        raise NotImplementedError()


###############################################################################
# Absence State Machine
###############################################################################


class AbsenceBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super().__init__(hpl_property, MonitorState.ACTIVE)

    @property
    def has_safe_state(self):
        return self.timeout >= 0 and self.timeout < INF and self.reentrant_scope

    def calc_pool_size(self, hpl_property):
        return 0

    def add_terminator(self, event):
        # must be called before pattern events
        v = None if self.reentrant_scope else True
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = TerminatorEvent(e.predicate, alias, v)
            states = self.on_msg[e.name]
            states[MonitorState.ACTIVE].append(datum)
            if self.has_safe_state:
                states[MonitorState.SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = BehaviourEvent(e.predicate, alias, None)
            self.on_msg[e.name][MonitorState.ACTIVE].append(datum)


###############################################################################
# Existence State Machine
###############################################################################


class ExistenceBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super().__init__(hpl_property, MonitorState.ACTIVE)

    def calc_pool_size(self, hpl_property):
        return 0

    def add_terminator(self, event):
        # must be called before pattern events
        self.has_safe_state = True
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            states = self.on_msg[e.name]
            datum = TerminatorEvent(e.predicate, alias, False)
            states[MonitorState.ACTIVE].append(datum)
            if self.reentrant_scope:
                datum = TerminatorEvent(e.predicate, alias, None)
                states[MonitorState.SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = BehaviourEvent(e.predicate, alias, None)
            self.on_msg[e.name][MonitorState.ACTIVE].append(datum)


###############################################################################
# Requirement State Machine
###############################################################################


class RequirementBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        self.has_trigger_refs = False
        self.dependent_predicates = defaultdict(HplVacuousTruth)
        self.trigger_is_simple = hpl_property.pattern.trigger.is_simple_event
        self._behaviour = None
        event = hpl_property.pattern.behaviour
        if event.is_simple_event:
            self._behaviour = event.alias
            if event.alias:
                for e in hpl_property.pattern.trigger.simple_events():
                    if e.contains_reference(event.alias):
                        self.has_trigger_refs = True
                        break
        super().__init__(hpl_property, MonitorState.ACTIVE)

    @property
    def has_safe_state(self):
        return (self.timeout > 0 or self.reentrant_scope) and not self.has_trigger_refs

    def calc_pool_size(self, hpl_property):
        if not self.has_trigger_refs:
            if self.timeout > 0:
                return 1
            else:
                return 0
        return -1

    def add_terminator(self, event):
        # must be called before pattern events
        v = None if self.reentrant_scope else True
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = TerminatorEvent(e.predicate, alias, v)
            states = self.on_msg[e.name]
            states[MonitorState.ACTIVE].append(datum)
            if self.has_safe_state:
                states[MonitorState.SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            # alias = None
            # if self._activator and e.contains_reference(self._activator):
            #    alias = self._activator
            # FIXME adding activator always to ensure dependent triggers have it
            datum = BehaviourEvent(e.predicate, self._activator, None)
            self.on_msg[e.name][MonitorState.ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            if self._behaviour:
                phi = e.predicate
                phi, psi = refactor_reference(phi, self._behaviour)
                if not psi.is_vacuous:
                    psi = replace_this_with_var(psi, '1')
                    psi = replace_var_with_this(psi, self._behaviour)
                    self.dependent_predicates[e.name] = psi
                datum = TriggerEvent(phi, alias)
            else:
                datum = TriggerEvent(e.predicate, alias)
            states = self.on_msg[e.name]
            states[MonitorState.ACTIVE].append(datum)
            if self.has_safe_state:
                states[MonitorState.SAFE].append(datum)


###############################################################################
# Response State Machine
###############################################################################


class ResponseBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super().__init__(hpl_property, MonitorState.SAFE)

    def calc_pool_size(self, hpl_property):
        if self._trigger:
            for e in hpl_property.pattern.behaviour.simple_events():
                if e.contains_reference(self._trigger):
                    return -1
        # no alias, no refs
        return 1 if self.timeout >= 0 else 0

    def add_terminator(self, event):
        # must be called before pattern events
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            states = self.on_msg[e.name]
            datum = TerminatorEvent(e.predicate, alias, False)
            states[MonitorState.ACTIVE].append(datum)
            if self.reentrant_scope:
                datum = TerminatorEvent(e.predicate, alias, None)
                states[MonitorState.SAFE].append(datum)
            else:
                datum = TerminatorEvent(e.predicate, alias, True)
                states[MonitorState.SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            activator = None
            if self._activator and e.contains_reference(self._activator):
                activator = self._activator
            trigger = None
            if self._trigger and e.contains_reference(self._trigger):
                trigger = self._trigger
            datum = BehaviourEvent(e.predicate, activator, trigger)
            self.on_msg[e.name][MonitorState.ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = TriggerEvent(e.predicate, alias)
            states = self.on_msg[e.name]
            if self.pool_size != 0:
                states[MonitorState.ACTIVE].append(datum)
            states[MonitorState.SAFE].append(datum)


###############################################################################
# Prevention State Machine
###############################################################################


class PreventionBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super().__init__(hpl_property, MonitorState.SAFE)

    def calc_pool_size(self, hpl_property):
        if self._trigger:
            for e in hpl_property.pattern.behaviour.simple_events():
                if e.contains_reference(self._trigger):
                    return -1
        # no alias, no refs
        return 1  # if self.timeout >= 0 else 0

    def add_terminator(self, event):
        # must be called before pattern events
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            if self.reentrant_scope:
                datum = TerminatorEvent(e.predicate, alias, None)
            else:
                datum = TerminatorEvent(e.predicate, alias, True)
            states = self.on_msg[e.name]
            states[MonitorState.ACTIVE].append(datum)
            states[MonitorState.SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            activator = None
            if self._activator and e.contains_reference(self._activator):
                activator = self._activator
            trigger = None
            if self._trigger and e.contains_reference(self._trigger):
                trigger = self._trigger
            datum = BehaviourEvent(e.predicate, activator, trigger)
            self.on_msg[e.name][MonitorState.ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = TriggerEvent(e.predicate, alias)
            states = self.on_msg[e.name]
            if self.pool_size != 0:
                states[MonitorState.ACTIVE].append(datum)
            states[MonitorState.SAFE].append(datum)
