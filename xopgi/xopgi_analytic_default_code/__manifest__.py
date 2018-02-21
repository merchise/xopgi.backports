#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_analytic_default_code',
    summary='Resurrects default of the code in analytic accounts',
    depends=['analytic'],
    installable=10 <= MAJOR_ODOO_VERSION < 11,  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
