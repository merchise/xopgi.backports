# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.backports
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2014-11-12


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
        'view/partner_merge_view.xml',  # noqa
        "view/%d/menu.xml" % MAJOR_ODOO_VERSION, # noqa
        'data/xopgi_partner_merge_cron.xml'  # noqa
    ],
    'application': False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    #
    # For Odoo 9+ we'll have to provide another solution.
    'installable':  8 <= MAJOR_ODOO_VERSION < 11,   # noqa

    'auto_install': False,
}
