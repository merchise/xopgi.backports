#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# __openerp__
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-20

dict(
    name='xopgi_fiscalyear',
    summary='Provides a unique API to get the fiscal year',
    depends=['account'],
    auto_install=False,
    application=False,
    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa
)
