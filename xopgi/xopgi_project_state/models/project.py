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
from xoeuf.models.proxy import ProjectProject as BaseProject


class Project(models.Model):
    _inherit = models.get_modelname(BaseProject)

    state = fields.Selection(
        selection=[('draft', 'New'),
                   ('open', 'In Progress'),
                   ('cancelled', 'Cancelled'),
                   ('pending', 'Pending'),
                   ('close', 'Closed')],
        string='Status',
        required=True,
        copy=False,
        default='open',
        track_visibility='onchange',
    )
