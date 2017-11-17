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
    name='xopgi_product_manager',
    summary='Recover the Product Manager',
    depends=['product'],
    data=[
        'view/%d/product_view.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],

    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa

    auto_install=False,
)
