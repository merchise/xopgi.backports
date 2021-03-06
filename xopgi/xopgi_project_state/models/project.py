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

    def set_done(self):
        return self.write(dict(state='close'))

    def set_cancel(self):
        return self.write(dict(state='cancelled'))

    def set_pending(self):
        return self.write(dict(state='pending'))

    def set_open(self):
        return self.write(dict(state='open'))
