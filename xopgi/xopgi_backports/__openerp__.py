#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

dict(
    name="Odoo backports and legacy features",

    # Since backports are only needed till OpenERP itself backports the
    # feature, the best strategy for versioning is using the latest date
    # **all** the ports are known to be missed.

    # Warning:  This addon should only contain res_config items.

    version="2017.09.20",

    author="Merchise Autrement",
    website="http://www.merchise.org/addons/xopgi_backports",
    category="Hidden",
    description="General fixes.",
    depends=['base', ],
    data=[
        'view/%d/config.xml' % ODOO_VERSION_INFO[0],   # noqa
        'view/%d/menu.xml'  % ODOO_VERSION_INFO[0],   # noqa
    ],
    application=False,

    # MIGRATION POLICY: All addons are not included until someone work on them
    # and upgrade them.
    installable=(8, 0) <= ODOO_VERSION_INFO < (11, 0),   # noqa

    auto_install=True,
)
