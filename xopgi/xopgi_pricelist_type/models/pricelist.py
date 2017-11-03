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
from xoeuf.models.proxy import ProductPricelist as BasePricelist


class ProductPricelistType(models.Model):
    _name = "product.pricelist.type"
    _description = "Pricelist Type"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    key = fields.Char(
        string='Key',
        required=True,
        help="Used in the code to select specific prices based on the context. Keep unchanged."
    )


class ProductPricelist(models.Model):
    _inherit = get_modelname(BasePricelist)
    _name = _inherit

    @api.model
    def _pricelist_type_get(self):
        pricelists = self.env['product.pricelist.type'].search([], order='name')
        return [(p.key, p.name) for p in pricelists]

    @api.model
    def _pricelist_type_default(self):
        pricelist_type1 = self.env['product.pricelist.type'].search([], limit=1)
        return pricelist_type1 and pricelist_type1.key or None

    type = fields.Selection(
        selection=_pricelist_type_get,
        string='Pricelist Type',
        default=_pricelist_type_default
    )
