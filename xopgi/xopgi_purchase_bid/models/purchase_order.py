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
from xoeuf.odoo import _
from xoeuf.models.proxy import PurchaseOrder
from xoeuf.odoo.exceptions import Warning as UserError


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

    # TODO: The method is completely redefined from the odoo because there is
    # no effective way to redefine it. The only change is the following:
    #
    # Odoo:
    # if order.state not in ['draft', 'sent']:
    #    continue
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'bid']:
                raise UserError(
                    _('Information!'),
                    _('The purchase order has to be in the Draft, Sent, Bid')
                )
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                   or (order.company_id.po_double_validation == 'two_step'\
                   and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                   or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return {}
