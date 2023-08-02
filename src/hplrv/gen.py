# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

"""
Module that contains the 'gen' command line program and the
high-level interface to generate runtime monitors from HPL properties.
"""

###############################################################################
# Imports
###############################################################################

from typing import Any, Dict, Final, Iterable, List, Optional, Type, Union

import argparse
from pathlib import Path

from attrs import field, frozen
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

###############################################################################
# Public Interface
###############################################################################


def monitors_from_files(paths: List[ANY_PATH], lang: str = 'py') -> List[str]:
    """
    Produces a list of monitor code snippets,
    given a list of paths to HPL files with specifications.
    """
    parser = specification_parser()
    r = MonitorGenerator(lang=lang)
    outputs: List[str] = []
    for input_path in paths:
        path: Path = Path(input_path).resolve(strict=True)
        text: str = path.read_text(encoding='utf-8').strip()
        spec: HplSpecification = parser.parse(text)
        for hpl_property in spec.properties:
            outputs.append(r.monitor_class(hpl_property))
    return outputs


def lib_from_files(paths: List[ANY_PATH], lang: str = 'py') -> str:
    """
    Produces a self-contained library of monitors,
    given a list of paths to HPL files with specifications.
    """
    parser = specification_parser()
    r = MonitorGenerator(lang=lang)
    properties: List[HplProperty] = []
    for input_path in paths:
        path: Path = Path(input_path).resolve(strict=True)
        text: str = path.read_text(encoding='utf-8').strip()
        spec: HplSpecification = parser.parse(text)
        properties.extend(spec.properties)
    return r.monitor_library(properties)


def monitors_from_spec(spec: ANY_SPEC, lang: str = 'py') -> List[str]:
    """
    Produces a list of monitor code snippets,
    given an HPL specification.
    """
    if not isinstance(spec, HplSpecification):
        parser = specification_parser()
        spec = parser.parse(spec)
    r = MonitorGenerator(lang=lang)
    outputs: List[str] = []
    for hpl_property in spec.properties:
        outputs.append(r.monitor_class(hpl_property))
    return outputs


def lib_from_spec(spec: ANY_SPEC, lang: str = 'py') -> str:
    """
    Produces a self-contained library of monitors,
    given an HPL specification.
    """
    if not isinstance(spec, HplSpecification):
        parser = specification_parser()
        spec = parser.parse(spec)
    r = MonitorGenerator(lang=lang)
    return r.monitor_library(spec.properties)


def monitor_from_property(property: ANY_PROP, lang: str = 'py') -> str:
    """
    Produces a monitor code snippet, given an HPL property.
    """
    if not isinstance(property, HplProperty):
        parser = property_parser()
        property = parser.parse(property)
    r = MonitorGenerator(lang=lang)
    return r.monitor_class(property)


def monitors_from_properties(properties: List[ANY_PROP], lang: str = 'py') -> List[str]:
    """
    Produces a list of monitor code snippets,
    given a list of HPL properties.
    """
    parser = property_parser()
    r = MonitorGenerator(lang=lang)
    outputs = []
    for property in properties:
        if not isinstance(property, HplProperty):
            property = parser.parse(property)
        outputs.append(r.monitor_class(property))
    return outputs


def lib_from_properties(properties: List[ANY_PROP], lang: str = 'py') -> str:
    """
    Produces a self-contained library of monitors,
    given a list of HPL properties.
    """
    parser = property_parser()
    r = MonitorGenerator(lang=lang)
    properties = [
        parser.parse(property)
        if not isinstance(property, HplProperty)
        else property
        for property in properties
    ]
    return r.monitor_library(properties)


@frozen
class TemplateRenderer:
    jinja_env: Environment

    @classmethod
    def from_pkg_data(
        cls,
        pkg: str = 'hplrv',
        template_dir: str = 'templates'
    ) -> 'TemplateRenderer':
        return cls(Environment(
            loader=PackageLoader(pkg, template_dir),
            line_statement_prefix=None,
            line_comment_prefix=None,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        ))

    def render_template(
        self,
        template_file: str,
        data: Dict[str, Any],
        strip: bool = True,
        encoding: Optional[str] = None
    ) -> str:
        template = self.jinja_env.get_template(template_file)
        text = template.render(**data)
        if strip:
            text = text.strip()
        if encoding is None:
            return text
        return text.encode(encoding)


@frozen
class MonitorGenerator:
    renderer: TemplateRenderer = field(factory=TemplateRenderer.from_pkg_data)
    lang: str = 'py'

    def monitor_library(
        self,
        spec_or_properties: Union[Iterable[HplProperty], HplSpecification],
    ) -> str:
        data = self.data_for_monitor_library(spec_or_properties)
        template_file = f'{self.lang}/library.{self.lang}.jinja'
        return self.renderer.render_template(template_file, data)

    def data_for_monitor_library(
        self,
        spec_or_properties: Union[Iterable[HplProperty], HplSpecification],
    ) -> Dict[str, Any]:
        class_names = []
        callbacks = {}
        monitor_classes = []
        if isinstance(spec_or_properties, HplSpecification):
            spec_or_properties = spec_or_properties.properties
        for p in spec_or_properties:
            builder, template_file = self._template(p, True)
            i = len(class_names)
            builder.class_name = f'Property{i}Monitor'
            class_names.append(builder.class_name)
            for name in builder.on_msg:
                if name not in callbacks:
                    callbacks[name] = set()
                callbacks[name].add(i)
            data = {'state_machine': builder}
            monitor_classes.append(self.renderer.render_template(template_file, data))
        return {
            'class_names': class_names,
            'monitor_classes': monitor_classes,
            'callbacks': callbacks,
        }

    def monitor_class(
        self,
        hpl_property: HplProperty,
        class_name: Optional[str] = None,
        id_as_class: bool = True,
        encoding: Optional[str] = None,
    ) -> str:
        data = self.data_for_monitor_class(
            hpl_property,
            class_name=class_name,
            id_as_class=id_as_class,
        )
        template_file = data['template_file']
        return self.renderer.render_template(template_file, data, encoding=encoding)

    def data_for_monitor_class(
        self,
        hpl_property: HplProperty,
        class_name: Optional[str] = None,
        id_as_class: bool = True,
    ) -> Dict[str, Any]:
        builder, template_file = self._template(hpl_property, id_as_class)
        if class_name:
            builder.class_name = class_name
        return {
            'template_file': template_file,
            'state_machine': builder,
        }

    def _template(self, hpl_property, id_as_class):
        if hpl_property.pattern.is_absence:
            builder = AbsenceBuilder(hpl_property)
            template_file = f'{self.lang}/absence.{self.lang}.jinja'
        elif hpl_property.pattern.is_existence:
            builder = ExistenceBuilder(hpl_property)
            template_file = f'{self.lang}/existence.{self.lang}.jinja'
        elif hpl_property.pattern.is_requirement:
            builder = RequirementBuilder(hpl_property)
            if not builder.has_trigger_refs:
                template_file = f'{self.lang}/requirement-simple.{self.lang}.jinja'
            else:
                template_file = f'{self.lang}/requirement-refs.{self.lang}.jinja'
        elif hpl_property.pattern.is_response:
            builder = ResponseBuilder(hpl_property)
            template_file = f'{self.lang}/response.{self.lang}.jinja'
        elif hpl_property.pattern.is_prevention:
            builder = PreventionBuilder(hpl_property)
            template_file = f'{self.lang}/prevention.{self.lang}.jinja'
        else:
            raise ValueError('unknown pattern: ' + str(hpl_property.pattern))
        if id_as_class:
            name = hpl_property.metadata.get('id', 'Property')
            name = ''.join(word.title() for word in name.split("_") if word)
            builder.class_name = name + 'Monitor'
        return (builder, template_file)


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
    lang: str = args['lang']
    if args.get('files'):
        if args.get('just_classes'):
            parts.extend(monitors_from_files(args['args'], lang=lang))
        else:
            parts.append(lib_from_files(args['args'], lang=lang))
    else:
        if args.get('just_classes'):
            parts.extend(monitors_from_properties(args['args'], lang=lang))
        else:
            parts.append(lib_from_properties(args['args'], lang=lang))
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
        '-c',
        '--class',
        dest='just_classes',
        action='store_true',
        help='output just the monitor classes (default: false)',
    )

    parser.add_argument(
        '-l',
        '--lang',
        choices=('py', 'js'),
        default='py',
        help='language of the generated code (default: py)',
    )

    parser.add_argument('args', nargs='+', help='input properties')

    args = parser.parse_args(args=argv)
    return vars(args)
