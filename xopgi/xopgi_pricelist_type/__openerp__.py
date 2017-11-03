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
    name='xopgi_pricelist_type',
    summary='Resurrects the type in product pricelists',
    depends=['product'],
    data=[
        'views/%d/pricelist_view.xml' % MAJOR_ODOO_VERSION,  # noqa
        'security/ir.model.access.csv',
        'data/pricelist_data.xml'
    ],

    # This is installable from Odoo 8+ just for us to be able to have it
    # installed before migrating the DB.  Otherwise, OpenUpgrade won't install
    # it and we may loose the data while migrating.
    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
