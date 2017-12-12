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


from xoeuf import models, fields, api, MAJOR_ODOO_VERSION
from xoeuf.models.proxy import PurchaseOrder


class PurchaseOrder(models.Model):
    _inherit = models.get_modelname(PurchaseOrder)

    bid_date = fields.Datetime(
        string='Bid Received On',
        readonly=True,
        help="Date on which the bid was received"
    )

    bid_validity = fields.Datetime(
        string='Bid Valid Until',
        help="Date on which the bid expire"
    )

    state = fields.Selection([
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('bid', 'Bid Received'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')])

    incoterm_id = fields.Many2one(
        'stock.incoterms',
        string="Incoterm",
        help=("International Commercial Terms are a series of predefined "
              "commercial terms used in international transactions.")
    )

    @api.multi
    def accion_bid_received(self):
        return self.write({'state': 'bid', 'bid_date': fields.Datetime.now()})

    @api.multi
    def button_confirm(self):
        approve = self.browse()
        for order in self:
            if order.state in ['draft', 'sent', 'bid']:
                approve |= order
                # Odoo 9+ skips orders that are not in 'draft', or 'sent'.  So
                # we trick it to process orders in state 'bid'.
                if order.state == 'bid':
                    order.state = 'sent'
        return super(PurchaseOrder, approve).button_confirm()
