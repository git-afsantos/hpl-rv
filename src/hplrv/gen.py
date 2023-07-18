# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gen' command line program and the
high-level interface to generate runtime monitors from HPL properties.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, List, Optional, Type, Union

import argparse
from pathlib import Path

from hpl.ast import HplProperty, HplSpecification
from hpl.parser import property_parser, specification_parser
from jinja2 import Environment, PackageLoader

from hplrv.monitors import (
    AbsenceBuilder,
    ExistenceBuilder,
    PreventionBuilder,
    RequirementBuilder,
    ResponseBuilder,
)

###############################################################################
# Constants
###############################################################################

PROG_GEN: Final[str] = 'hpl-rv gen'

ANY_PATH: Final[Type] = Union[Path, str]
ANY_SPEC: Final[Type] = Union[HplSpecification, str]
ANY_PROP: Final[Type] = Union[HplProperty, str]

TEMPLATE_MONITOR: Final[str] = 'class'
TEMPLATE_LIBRARY: Final[str] = 'lib'
TEMPLATE_ROSNODE: Final[str] = 'ros'
TEMPLATE_ROS2NODE: Final[str] = 'ros2'

###############################################################################
# Public Interface
###############################################################################


def monitors_from_files(paths: List[ANY_PATH]) -> List[str]:
    """
    Produces a list of monitor code snippets,
    given a list of paths to HPL files with specifications.
    """
    parser = specification_parser()
    r = TemplateRenderer()
    outputs: List[str] = []
    for input_path in paths:
        path: Path = Path(input_path).resolve(strict=True)
        text: str = path.read_text(encoding='utf-8').strip()
        spec: HplSpecification = parser.parse(text)
        for hpl_property in spec.properties:
            outputs.append(r.render_monitor(hpl_property))
    return outputs


def lib_from_files(paths: List[ANY_PATH]) -> str:
    """
    Produces a self-contained library of monitors,
    given a list of paths to HPL files with specifications.
    """
    parser = specification_parser()
    r = TemplateRenderer()
    properties: List[HplProperty] = []
    for input_path in paths:
        path: Path = Path(input_path).resolve(strict=True)
        text: str = path.read_text(encoding='utf-8').strip()
        spec: HplSpecification = parser.parse(text)
        properties.extend(spec.properties)
    return r.render_monitor_library(properties)


def monitors_from_spec(spec: ANY_SPEC) -> List[str]:
    """
    Produces a list of monitor code snippets,
    given an HPL specification.
    """
    if not isinstance(spec, HplSpecification):
        parser = specification_parser()
        spec = parser.parse(spec)
    r = TemplateRenderer()
    outputs: List[str] = []
    for hpl_property in spec.properties:
        outputs.append(r.render_monitor(hpl_property))
    return outputs


def lib_from_spec(spec: ANY_SPEC) -> str:
    """
    Produces a self-contained library of monitors,
    given an HPL specification.
    """
    if not isinstance(spec, HplSpecification):
        parser = specification_parser()
        spec = parser.parse(spec)
    r = TemplateRenderer()
    return r.render_monitor_library(spec.properties)


def monitor_from_property(property: ANY_PROP) -> str:
    """
    Produces a monitor code snippet, given an HPL property.
    """
    if not isinstance(property, HplProperty):
        parser = property_parser()
        property = parser.parse(property)
    r = TemplateRenderer()
    return r.render_monitor(property)


def monitors_from_properties(properties: List[ANY_PROP]) -> List[str]:
    """
    Produces a list of monitor code snippets,
    given a list of HPL properties.
    """
    parser = property_parser()
    r = TemplateRenderer()
    outputs = []
    for property in properties:
        if not isinstance(property, HplProperty):
            property = parser.parse(property)
        outputs.append(r.render_monitor(property))
    return outputs


def lib_from_properties(properties: List[ANY_PROP]) -> str:
    """
    Produces a self-contained library of monitors,
    given a list of HPL properties.
    """
    parser = property_parser()
    r = TemplateRenderer()
    properties = [
        parser.parse(property)
        if not isinstance(property, HplProperty)
        else property
        for property in properties
    ]
    return r.render_monitor_library(properties)


class TemplateRenderer:
    def __init__(self):
        self.jinja_env = Environment(
            loader=PackageLoader('hplrv', 'templates'),
            line_statement_prefix=None,
            line_comment_prefix=None,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

    def render_monitor_library(self, hpl_properties):
        class_names = []
        callbacks = {}
        monitor_classes = []
        for p in hpl_properties:
            builder, template_file = self._template(p, True)
            i = len(class_names)
            builder.class_name = f'Property{i}Monitor'
            class_names.append(builder.class_name)
            for name in builder.on_msg:
                if name not in callbacks:
                    callbacks[name] = set()
                callbacks[name].add(i)
            data = {'state_machine': builder}
            monitor_classes.append(self._render_template(template_file, data))
        data = {
            'class_names': class_names,
            'monitor_classes': monitor_classes,
            'callbacks': callbacks,
        }
        return self._render_template('library.python.jinja', data)

    def render_rospy_node(self, hpl_properties, topic_types):
        class_names = []
        topics = {}
        callbacks = {}
        monitor_classes = []
        for p in hpl_properties:
            builder, template_file = self._template(p, True)
            i = len(class_names)
            builder.class_name = f'Property{i}Monitor'
            class_names.append(builder.class_name)
            for name in builder.on_msg:
                topics[name] = topic_types[name]
                if name not in callbacks:
                    callbacks[name] = set()
                callbacks[name].add(i)
            data = {'state_machine': builder}
            monitor_classes.append(self._render_template(template_file, data))
        ros_imports = {'std_msgs'}
        for name in topics.values():
            pkg, msg = name.split('/')
            ros_imports.add(pkg)
        data = {
            'class_names': class_names,
            'monitor_classes': monitor_classes,
            'topics': topics,
            'ros_imports': ros_imports,
            'callbacks': callbacks,
        }
        return self._render_template('rosnode.python.jinja', data)

    def render_monitor(self, hpl_property, class_name=None, id_as_class=True, encoding=None):
        builder, template_file = self._template(hpl_property, id_as_class)
        if class_name:
            builder.class_name = class_name
        data = {'state_machine': builder}
        return self._render_template(template_file, data, encoding=encoding)

    def _template(self, hpl_property, id_as_class):
        if hpl_property.pattern.is_absence:
            builder = AbsenceBuilder(hpl_property)
            template_file = 'absence.python.jinja'
        elif hpl_property.pattern.is_existence:
            builder = ExistenceBuilder(hpl_property)
            template_file = 'existence.python.jinja'
        elif hpl_property.pattern.is_requirement:
            builder = RequirementBuilder(hpl_property)
            if not builder.has_trigger_refs:
                template_file = 'requirement-simple.python.jinja'
            else:
                template_file = 'requirement-refs.python.jinja'
        elif hpl_property.pattern.is_response:
            builder = ResponseBuilder(hpl_property)
            template_file = 'response.python.jinja'
        elif hpl_property.pattern.is_prevention:
            builder = PreventionBuilder(hpl_property)
            template_file = 'prevention.python.jinja'
        else:
            raise ValueError('unknown pattern: ' + str(hpl_property.pattern))
        if id_as_class:
            name = hpl_property.metadata.get('id', 'Property')
            name = ''.join(word.title() for word in name.split("_") if word)
            builder.class_name = name + 'Monitor'
        return (builder, template_file)

    def _render_template(self, template_file, data, strip=True, encoding=None):
        template = self.jinja_env.get_template(template_file)
        text = template.render(**data)
        if strip:
            text = text.strip()
        if encoding is None:
            return text
        return text.encode(encoding)


###############################################################################
# Entry Point
###############################################################################


def subprogram(
    argv: Optional[List[str]],
    _settings: Optional[Dict[str, Any]] = None,
) -> int:
    args = parse_arguments(argv)
    return run(args, _settings or {})


def run(args: Dict[str, Any], _settings: Dict[str, Any]) -> int:
    parts: List[str] = []
    if args.get('files'):
        parts.extend(monitors_from_files(args['args']))
    else:
        parts.extend(monitors_from_properties(args['args']))
    output: str = '\n\n'.join(code for code in parts)

    input_path: str = args.get('output')
    if input_path:
        path: Path = Path(input_path).resolve(strict=False)
        path.write_text(output, encoding='utf-8')
    else:
        print(output)
    return 0


###############################################################################
# Argument Parsing
###############################################################################


def parse_arguments(argv: Optional[List[str]]) -> Dict[str, Any]:
    description = 'Generate runtime monitors from HPL properties.'
    parser = argparse.ArgumentParser(prog=PROG_GEN, description=description)

    parser.add_argument('-o', '--output', help='output file to place generated code')

    parser.add_argument(
        '-f',
        '--files',
        action='store_true',
        help='process args as HPL files (default: HPL properties)',
    )

    parser.add_argument(
        '-t',
        '--template',
        default=TEMPLATE_MONITOR,
        choices=[TEMPLATE_MONITOR, TEMPLATE_LIBRARY, TEMPLATE_ROSNODE, TEMPLATE_ROS2NODE],
        help='which template to use for generated code (default: class)',
    )

    parser.add_argument('args', nargs='+', help='input properties')

    args = parser.parse_args(args=argv)
    return vars(args)
