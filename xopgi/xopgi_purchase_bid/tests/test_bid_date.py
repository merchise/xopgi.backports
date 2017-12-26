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

from xoeuf import fields
from xoeuf.odoo.tests.common import TransactionCase


class TestBidDateReceived(TransactionCase):
    def setUp(self):
        super(TestBidDateReceived, self).setUp()
        purchase_order = self.env['purchase.order']
        partner = self.env['res.partner'].search(
            [('supplier', '=', True)],
            limit=1
        )

        values = dict(
            partner_id=partner.id,
            date_planned=fields.Datetime.now(),
            date_order=fields.Datetime.now(),
        )
        self.order = purchase_order.create(values)
        self.order.write({'state': 'sent'})

    def test_bid_date(self):
        self.order.accion_bid_received()
        self.assertEqual(self.order.state, 'bid')
        self.assertTrue(self.order.bid_date)
