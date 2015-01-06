# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.backports
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2014-11-12


{
    "name": "ERP backports, Partner Merge",

    "version": "2014.11.12",

    "author": "Merchise Autrement",
    "website": "http://www.merchise.org/addons/xopgi_backports/partner_merge",
    "category": "Hidden",
    "description": "General fixes.",
    "depends": ['base', 'crm'],
    "data": [
        'init/metaphone.xml',
        'view/base_partner_merge_view.xml'
            if ODOO_VERSION_INFO < (8, 0) else 'dummy.xml',
        'security/base_partner_merge.xml'
            if ODOO_VERSION_INFO < (8, 0) else 'dummy.xml',
    ],
    "demo_xml": [],
    "css": [],
    "application": False,
    "installable": True,
    'auto_install': False,
}
