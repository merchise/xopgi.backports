#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

{
    'name': "ERP backports, Partner Merge",
    'version': "2015.06.01",
    'author': "Merchise Autrement",
    'website': "http://www.merchise.org/addons/xopgi_backports/partner_merge",
    'category': "Hidden",
    'description': "General fixes.",

    'depends': list(filter(bool, [
        'base',
        'crm',
        'xopgi_object_merger',
    ])),

    'data': [
        'init/metaphone.xml',  # noqa
        'security/xopgi_partner_merge.xml',  # noqa
        'security/ir.model.access.csv',  # noqa
        'view/partner_merge_view.xml',  # noqa
        'view/menu.xml',  # noqa
        'data/xopgi_partner_merge_cron.xml'  # noqa
    ],
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # For Odoo 9+ we'll have to provide another solution.
    'installable':  9 < MAJOR_ODOO_VERSION < 11,   # noqa

    'auto_install': False,
}
