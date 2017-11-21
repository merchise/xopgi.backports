#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

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
