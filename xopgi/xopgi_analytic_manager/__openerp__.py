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
# Created on 2017-06-21

dict(
    name='xopgi_analytic_manager',
    summary='Resurrects the manager_id in analytic accounts',
    depends=['analytic'],
    installable=(9, 0) <= ODOO_VERSION_INFO < (10, 0),  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
