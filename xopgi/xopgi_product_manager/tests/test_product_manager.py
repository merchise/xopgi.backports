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


class TestProductManager(TransactionCase):

    def setUp(self):
        super(TestProductManager, self).setUp()
        product = self.env['product.product']
        user = self.env['res.users']
        self.user = user.create({'name': 'Hello World',
                                 'login': 'hello@world'})
        self.product = product.create({'name': 'Test products',
                                       'product_manager': self.user.id})
        self.manager = self.product.mapped('product_manager.id')

    def test_field_exists(self):
        m = len(self.manager)
        self.assertGreater(m, 0)
