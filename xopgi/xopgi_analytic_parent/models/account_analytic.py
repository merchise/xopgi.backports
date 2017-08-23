#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# analytic
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-08-16


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from xoeuf import models, fields, api
from xoeuf.models import get_modelname
from xoeuf.models.proxy import AccountAnalyticAccount


class AnalyticAccount(models.Model):
    _inherit = get_modelname(AccountAnalyticAccount)

    parent_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Parent Analytic Account',
        select=2
    )
    child_ids = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='parent_id',
        string='Child Accounts'
    )

    @api.multi
    def check_recursion(self, parent=None):
        return super(AnalyticAccount, self)._check_recursion(parent=parent)

    _constraints = [
        (check_recursion, 'Error! You cannot create recursive analytic accounts.', ['parent_id']),
    ]
