#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_imports)


def read_terpfile():
    import os
    from os.path import join
    with open(join(os.path.dirname(__file__), '__openerp__.py'), 'rU') as fh:
        content = fh.read()
        # Odoo version doesn't really matter here.  But we need to provide a
        # fake one for the `eval` to succeed.
        fake = {'ODOO_VERSION_INFO': (7, 0)}
        return eval(content, fake, {})


_TERP = read_terpfile()
VERSION = _TERP['version']
