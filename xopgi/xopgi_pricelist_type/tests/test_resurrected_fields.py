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
from xoeuf.models.proxy import ProductPricelist as Pricelist
from xoeuf.models.proxy import ProductPricelistType as PricelistType
from xoeuf.models import get_modelname


class TestResurrectedFields(object):
    def test_model_has_resurrected_fields(self):
        for attr in self.resurrected_fields:
            self.assertTrue(hasattr(self.Model, attr), msg='Missing %s' % attr)

    def test_views_load(self):
        from xoeuf.models.extensions import get_treeview_action
        self.Model.search([], limit=1).get_formview_action()
        get_treeview_action(self.Model.search([], limit=1))


class TestTypeField(TransactionCase, TestResurrectedFields):
    def setUp(self):
        super(TestTypeField, self).setUp()
        self.Model = self.env[get_modelname(Pricelist)]
        self.resurrected_fields = ['type', ]


class TestPricelistTypeFields(TransactionCase, TestResurrectedFields):
    def setUp(self):
        super(TestPricelistTypeFields, self).setUp()
        self.Model = self.env[get_modelname(PricelistType)]
        self.resurrected_fields = ['name', 'key', ]
