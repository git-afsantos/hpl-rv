# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

from collections import defaultdict, namedtuple

from hpl.ast import HplVacuousTruth
from hpl.logic import refactor_reference, replace_this_with_var, replace_var_with_this

from hplrv.constants import (
    EVENT_ACTIVATOR,
    EVENT_BEHAVIOUR,
    EVENT_OTHER,
    EVENT_TERMINATOR,
    EVENT_TRIGGER,
    INF,
    STATE_ACTIVE,
    STATE_FALSE,
    STATE_INACTIVE,
    STATE_OFF,
    STATE_SAFE,
    STATE_TRUE,
)

###############################################################################
# Data Structures
###############################################################################

ActivatorEvent = namedtuple('ActivatorEvent', ('event_type', 'predicate'))


def new_activator(phi):
    # phi: HplPredicate
    return ActivatorEvent(EVENT_ACTIVATOR, phi)


TerminatorEvent = namedtuple('TerminatorEvent', ('event_type', 'predicate', 'activator', 'verdict'))


def new_terminator(phi, activator, verdict):
    # predicate: HplPredicate
    # activator: str|None
    # verdict: bool|None
    return TerminatorEvent(EVENT_TERMINATOR, phi, activator, verdict)


BehaviourEvent = namedtuple('BehaviourEvent', ('event_type', 'predicate', 'activator', 'trigger'))


def new_behaviour(phi, activator, trigger):
    # predicate: HplPredicate
    # activator: str|None
    # trigger: str|None
    return BehaviourEvent(EVENT_BEHAVIOUR, phi, activator, trigger)


TriggerEvent = namedtuple('TriggerEvent', ('event_type', 'predicate', 'activator'))


def new_trigger(phi, activator):
    # predicate: HplPredicate
    # activator: str|None
    return TriggerEvent(EVENT_TRIGGER, phi, activator)


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
        elif hpl_property.scope.is_after:
            self.initial_state = STATE_INACTIVE
            self.add_activator(hpl_property.scope.activator)
        elif hpl_property.scope.is_until:
            self.initial_state = s0
            self.add_terminator(hpl_property.scope.terminator)
        elif hpl_property.scope.is_after_until:
            self.initial_state = STATE_INACTIVE
            self.reentrant_scope = True
            self.add_activator(hpl_property.scope.activator)
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
            datum = new_activator(e.predicate)
            self.on_msg[e.topic][STATE_INACTIVE].append(datum)

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
        super(AbsenceBuilder, self).__init__(hpl_property, STATE_ACTIVE)

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
            datum = new_terminator(e.predicate, alias, v)
            states = self.on_msg[e.topic]
            states[STATE_ACTIVE].append(datum)
            if self.has_safe_state:
                states[STATE_SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = new_behaviour(e.predicate, alias, None)
            self.on_msg[e.topic][STATE_ACTIVE].append(datum)


###############################################################################
# Existence State Machine
###############################################################################


class ExistenceBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super(ExistenceBuilder, self).__init__(hpl_property, STATE_ACTIVE)

    def calc_pool_size(self, hpl_property):
        return 0

    def add_terminator(self, event):
        # must be called before pattern events
        self.has_safe_state = True
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            states = self.on_msg[e.topic]
            datum = new_terminator(e.predicate, alias, False)
            states[STATE_ACTIVE].append(datum)
            if self.reentrant_scope:
                datum = new_terminator(e.predicate, alias, None)
                states[STATE_SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = new_behaviour(e.predicate, alias, None)
            self.on_msg[e.topic][STATE_ACTIVE].append(datum)


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
        super(RequirementBuilder, self).__init__(hpl_property, STATE_ACTIVE)

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
            datum = new_terminator(e.predicate, alias, v)
            states = self.on_msg[e.topic]
            states[STATE_ACTIVE].append(datum)
            if self.has_safe_state:
                states[STATE_SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            # alias = None
            # if self._activator and e.contains_reference(self._activator):
            #    alias = self._activator
            # FIXME adding activator always to ensure dependent triggers have it
            datum = new_behaviour(e.predicate, self._activator, None)
            self.on_msg[e.topic][STATE_ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            if self._behaviour:
                phi = e.predicate.clone()
                phi, psi = refactor_reference(phi, self._behaviour)
                if not psi.is_vacuous:
                    replace_this_with_var(psi, '1')
                    replace_var_with_this(psi, self._behaviour)
                    self.dependent_predicates[e.topic] = psi
                datum = new_trigger(phi, alias)
            else:
                datum = new_trigger(e.predicate, alias)
            states = self.on_msg[e.topic]
            states[STATE_ACTIVE].append(datum)
            if self.has_safe_state:
                states[STATE_SAFE].append(datum)


###############################################################################
# Response State Machine
###############################################################################


class ResponseBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super(ResponseBuilder, self).__init__(hpl_property, STATE_SAFE)

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
            states = self.on_msg[e.topic]
            datum = new_terminator(e.predicate, alias, False)
            states[STATE_ACTIVE].append(datum)
            if self.reentrant_scope:
                datum = new_terminator(e.predicate, alias, None)
                states[STATE_SAFE].append(datum)
            else:
                datum = new_terminator(e.predicate, alias, True)
                states[STATE_SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            activator = None
            if self._activator and e.contains_reference(self._activator):
                activator = self._activator
            trigger = None
            if self._trigger and e.contains_reference(self._trigger):
                trigger = self._trigger
            datum = new_behaviour(e.predicate, activator, trigger)
            self.on_msg[e.topic][STATE_ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = new_trigger(e.predicate, alias)
            states = self.on_msg[e.topic]
            if self.pool_size != 0:
                states[STATE_ACTIVE].append(datum)
            states[STATE_SAFE].append(datum)


###############################################################################
# Prevention State Machine
###############################################################################


class PreventionBuilder(PatternBasedBuilder):
    def __init__(self, hpl_property):
        super(PreventionBuilder, self).__init__(hpl_property, STATE_SAFE)

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
                datum = new_terminator(e.predicate, alias, None)
            else:
                datum = new_terminator(e.predicate, alias, True)
            states = self.on_msg[e.topic]
            states[STATE_ACTIVE].append(datum)
            states[STATE_SAFE].append(datum)

    def add_behaviour(self, event):
        for e in event.simple_events():
            activator = None
            if self._activator and e.contains_reference(self._activator):
                activator = self._activator
            trigger = None
            if self._trigger and e.contains_reference(self._trigger):
                trigger = self._trigger
            datum = new_behaviour(e.predicate, activator, trigger)
            self.on_msg[e.topic][STATE_ACTIVE].append(datum)

    def add_trigger(self, event):
        for e in event.simple_events():
            alias = None
            if self._activator and e.contains_reference(self._activator):
                alias = self._activator
            datum = new_trigger(e.predicate, alias)
            states = self.on_msg[e.topic]
            if self.pool_size != 0:
                states[STATE_ACTIVE].append(datum)
            states[STATE_SAFE].append(datum)
