#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name='xopgi_analytic_sale_contracts',
    summary='Resurrects the tree view of analytic accounts (contracts) in sale menu.',
    depends=list(filter(bool, [
        'analytic',
        'sales_team',

        # Resurrects the state in analytic accounts in Odoo 9 and 10.
        'xopgi_analytic_state' if MAJOR_ODOO_VERSION > 8 else None,  # noqa

        # Resurrects the manager_id in analytic accounts in Odoo 9 and 10.
        'xopgi_analytic_manager' if MAJOR_ODOO_VERSION > 8 else None,  # noqa

        # Resurrects the dates in analytic accounts in Odoo 9 and 10.
        'xopgi_analytic_dates' if MAJOR_ODOO_VERSION > 8 else None,  # noqa

        # Resurrects the parent in analytic accounts in Odoo 9 and 10.
        'xopgi_analytic_parent' if MAJOR_ODOO_VERSION > 8 else None,  # noqa
        ])),
    data=[
        'views/%d/account_analytic_analysis_view.xml' % MAJOR_ODOO_VERSION,  # noqa
    ],

    # This is installable from Odoo 8+ just for us to be able to have it
    # installed before migrating the DB.  Otherwise, OpenUpgrade won't install
    # it and we may loose the data while migrating.
    installable=8 <= MAJOR_ODOO_VERSION < 11,  # noqa

    # Only install this, if someone requires it.
    auto_install=False,
)
