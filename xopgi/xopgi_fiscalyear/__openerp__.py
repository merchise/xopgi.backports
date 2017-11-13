#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_fiscalyear',
    summary='Provides a unique API to get the fiscal year',
    depends=['account'],
    auto_install=False,
    application=False,
    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa
)
