#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_mrp_bom_line_type',
    summary='Resurrect the type BoM line in the BoM lines',
    depends=['mrp'],
    data=list(filter(bool, [
        'views/bom_lines_view.xml' if MAJOR_ODOO_VERSION > 8 else None,  # noqa
    ])),


    # This is installable from Odoo 8+ just for us to be able to have it
    # installed before migrating the DB.  Otherwise, OpenUpgrade won't install
    # it and we may loose the data while migrating.
    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
