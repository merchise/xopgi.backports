# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.backports
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2014-11-12


{
    "name": "ERP backports, Partner Merge",

    "version": "2015.06.01",

    "author": "Merchise Autrement",
    "website": "http://www.merchise.org/addons/xopgi_backports/partner_merge",
    "category": "Hidden",
    "description": "General fixes.",
    "depends": ['base', 'crm'],
    "data": [
        'init/metaphone.xml',
        'view/xopgi_partner_merge_view.xml',
        'security/xopgi_partner_merge.xml',
    ],
    "demo_xml": [],
    "css": [],
    "application": False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    'installable': (8, 0) <= ODOO_VERSION_INFO < (9, 0),   # noqa

    'auto_install': False,
}
