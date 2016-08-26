# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.backports.config
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-11-12

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from openerp.osv import fields, orm


class XopgiBackportConfig(orm.TransientModel):
    _name = 'xopgi.backports.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'module_xopgi_partner_merge':
            fields.boolean("Allow to merger partners",
                           help="Install the module xopgi_partner_merge, "
                           "which is a backport from Odoo's similar feature.")
    }
