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
from xoeuf.models.proxy import ProductPricelist as Model
from xoeuf.models.proxy import ProductPricelistType as Model2
from xoeuf.models import get_modelname


class TestFieldsExist(TransactionCase):
    def setUp(self):
        super(TestFieldsExist, self).setUp()
        self.Model = self.env[get_modelname(Model)]
        self.resurrected_fields = ['type', ]

    def test_fields_exists(self):
        for attr in self.resurrected_fields:
            self.assertTrue(hasattr(self.Model, attr), msg='Missing %s' % attr)

    def test_views_load(self):
        from xoeuf.models.extensions import get_treeview_action
        self.Model.search([], limit=1).get_formview_action()
        get_treeview_action(self.Model.search([], limit=1))


class TestFieldsExist2(TransactionCase):
    def setUp(self):
        super(TestFieldsExist, self).setUp()
        self.Model = self.env[get_modelname(Model2)]
        self.resurrected_fields = ['name', 'key', ]

    def test_fields_exists(self):
        self.assertTrue(
            all(hasattr(self.Model, attr) for attr in self.resurrected_fields)
        )

    def test_views_load(self):
        from xoeuf.models.extensions import get_treeview_action
        self.Model.search([]).get_formview_action()
        get_treeview_action(self.Model.search([]))
