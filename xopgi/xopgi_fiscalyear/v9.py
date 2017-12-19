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


class Company(models.Model):
    _inherit = 'res.company'

    @api.requires_singleton
    def get_fiscal_year(self, ref=None):
        '''Get the fiscal year containing a reference date for the company.

        Return a `xoutil.future.datetime.TimeSpan`:class: with the fiscal year
        containing `ref`.  If `ref` is None, use today.

        '''
        from xoutil.future.datetime import date, TimeSpan
        res = self.compute_fiscalyear_dates(ref or date.today())
        return TimeSpan(res['date_from'], res['date_to'])
