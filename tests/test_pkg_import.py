# SPDX-License-Identifier: MIT
# Copyright © 2023 André Santos

###############################################################################
# Imports
###############################################################################

import hplrv

###############################################################################
# Tests
###############################################################################


def test_import_was_ok():
    assert True


def test_pkg_has_version():
    assert hasattr(hplrv, '__version__')
    assert isinstance(hplrv.__version__, str)
    assert hplrv.__version__ != ''
