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


from xoeuf.odoo import _
from xoeuf import models, fields, api
from xoeuf.models import get_modelname
from xoeuf.models.proxy import ProductPricelistItem as BasePricelistItem


class PriceType(models.Model):
    """The price type is used to points which field in the product form is a price
       and in which currency is this price expressed.  When a field is a
       price, you can use it in pricelists to base sale and purchase prices
       based on some fields of the product.

    """
    _name = "product.price.type"
    _description = "Price Type"

    @api.model
    def _get_currency(self):
        comp = self.env.user.company_id
        if not comp:
            comp = self.env['res.company'].search([], limit=1)
        return comp.currency_id.id

    active = fields.Boolean(
        string="Active",
        default=True
    )
    name = fields.Char(
        string='Price Name',
        required=True,
        translate=True,
        help="Name of this kind of price."
    )
    field = fields.Selection(
        selection="_price_field_get",
        string="Product Field",
        size=32,
        required=True,
        help="Associated field in the product form."
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        required=True,
        default=_get_currency,
        help="The currency the field is expressed in."
    )

    @api.model
    def _price_field_get(self):
        mf = self.env['ir.model.fields']
        fields = mf.search(
            [('model', 'in', (('product.product'), ('product.template'))),
             ('ttype', '=', 'float')]
        )
        res = []
        for field in fields:
            if not (field.name, field.field_description) in res:
                res.append((field.name, field.field_description))
        return res


class ProductPricelistItem(models.Model):
    _inherit = get_modelname(BasePricelistItem)
    _name = _inherit

    @api.model
    def _get_price_field_get(self):
        PriceType = self.env['product.price.type']
        types = PriceType.search([])
        result = []
        for line in types:
            result.append((line.field, line.name))
        result.append(('pricelist', _('Other Pricelist')))
        return result

    base = fields.Selection(
        selection="_get_price_field_get",
        string="Based on",
        required=True,
        default="list_price",
        help="Base price for computation."
    )
