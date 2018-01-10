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

from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.models.proxy import AccountAnalyticAccount as Model
from xoeuf.models import get_modelname


class TestFieldsView(TransactionCase):
    def setUp(self):
        super(TestFieldsView, self).setUp()
        self.Model = self.env[get_modelname(Model)]
        group_user = self.env.ref('sales_team.group_sale_salesman')
        self.user = self.env['res.users'].create({
            'name': 'Mark User',
            'login': 'user',
            'email': 'm.u@example.com',
            'signature': '--\nMark',
            'notify_email': 'always',
            'groups_id': [(6, 0, [group_user.id])]
        })

    def test_views_load(self):
        from xoeuf.models.extensions import get_treeview_action
        self.Model.search([], limit=1).get_formview_action()
        get_treeview_action(self.Model.search([], limit=1))

    def test_salesman_access_rights_2_analytic_account(self):
        self.Model.sudo(self.user.id).search([])
