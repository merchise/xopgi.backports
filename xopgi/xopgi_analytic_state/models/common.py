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

from xoeuf import models, api
from xoeuf.models.proxy import AccountAnalyticAccount


class AnalyticAccount(models.Model):
    _inherit = models.get_modelname(AccountAnalyticAccount)

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def set_pending(self):
        return self.write({'state': 'pending'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancelled'})
