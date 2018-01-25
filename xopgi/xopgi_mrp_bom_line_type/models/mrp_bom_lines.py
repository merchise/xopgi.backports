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


from xoeuf import models, fields
from xoeuf.models.proxy import MrpBomLine as BomLines


class MrpBomLine(models.Model):
    _inherit = models.get_modelname(BomLines)

    type = fields.Selection(
        [('normal', 'Manufacture this product'),
         ('phantom', 'Ship this product as a set of components (kit)')],
        string='BoM Type',
        default='normal',
        required=True,
        help=("Kit (Phantom): When processing a sales order for this product, "
              "the delivery order will contain the raw materials,"
              "instead of the finished product.")
    )
