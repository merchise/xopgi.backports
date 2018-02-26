#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_project_state',
    summary='Resurrects the state in projects',
    depends=['project'],
    data=[
        'views/project.xml',
    ],

    # This is installable from Odoo 8+ just for us to be able to have it
    # installed before migrating the DB.  Otherwise, OpenUpgrade won't install
    # it and we may loose the data while migrating.
    installable=10 <= MAJOR_ODOO_VERSION < 11,  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
