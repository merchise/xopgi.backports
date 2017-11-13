#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoeuf import ODOO_VERSION_INFO
from xoeuf import models, fields
from xoeuf.models.proxy import AccountAnalyticAccount

if (9, 0) <= ODOO_VERSION_INFO < (11, 0):
    class AnalyticAccount(models.Model):
        _inherit = models.get_modelname(AccountAnalyticAccount)

        manager_id = fields.Many2one(
            'res.users',
            'Account Manager',
            track_visibility='onchange'
        )
