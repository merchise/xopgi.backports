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
    "name": "ERP backports (xopgi)",

    # Since backports are only needed till OpenERP itself backports the
    # feature, the best strategy for versioning is using the latest date
    # **all** the ports are known to be missed.

    # Warning:  This addon should only contain res_config items.

    "version": "2015.06.01",

    "author": "Merchise Autrement",
    "website": "http://www.merchise.org/addons/xopgi_backports",
    "category": "Hidden",
    "description": "General fixes.",
    "depends": ['base', ],
    "data": [
        'view/config.xml',
    ],
    "application": False,
    "installable": True,
    'auto_install': True,
}
