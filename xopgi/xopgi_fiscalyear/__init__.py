#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-20

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import MAJOR_ODOO_VERSION

if 8 <= MAJOR_ODOO_VERSION < 11:
    from . import common # noqa
    if MAJOR_ODOO_VERSION == 8:
        from . import v8  # noqa
    elif MAJOR_ODOO_VERSION == 9:
        from . import v9  # noqa
    elif MAJOR_ODOO_VERSION == 10:
        from . import v10  # noqa
else:
    raise NotImplementedError
