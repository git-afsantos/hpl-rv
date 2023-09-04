# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v1.1.2](https://github.com/git-afsantos/hpl-rv/releases/tag/v1.1.2) - 2023-09-04
### Changed
- Updated GitHub workflows.

## [v1.1.1](https://github.com/git-afsantos/hpl-rv/releases/tag/v1.1.1) - 2023-09-04
### Fixed
- Updated code to be compatible with HPL `v1.1`.

## [v1.1.0](https://github.com/git-afsantos/hpl-rv/releases/tag/v1.1.0) - 2023-08-03
### Added
- Templates to generate monitors in JavaScript.
- A `--lang` option for the `gen` command to choose output language (choices: `py`, `js`; default: `py`).

## [v1.0.0](https://github.com/git-afsantos/hpl-rv/releases/tag/v1.0.0) - 2023-07-31
Initial release of the package, upgraded from the previous repository: `hpl-rv-gen`.

Includes a CLI script with:

- a `gen` subprogram to generate runtime monitors;
- a `gui` subprogram to serve a web dashboard to visualize monitor status in real time;
- a `play` subprogram to load generated monitors and replay a trace of messages (useful to test the `gui` dashboard).

## [v0.0.0](https://github.com/git-afsantos/hpl-rv/releases/tag/v0.0.0) - 2023-07-12
Repository creation.
