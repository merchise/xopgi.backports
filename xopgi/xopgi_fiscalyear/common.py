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

from xoeuf import models


class AccountConfigFiscalYear(models.TransientModel):
    _inherit = 'account.config.settings'

    # Fiscal Years and Periods in Odoo 9 have been replaced with a single setting
    # "Fiscal Year Last Day".  To see: Accounting/Configuration/Settings So if
    # "Fiscal Year Last Day" is set to sept 30, then each oct 1st a new Fiscal
    # Year would.
    def get_fiscal_year(self, ref=None):
        '''Get the fiscal year containing a reference date.

        Return a `xoutil.datetime.TimeSpan`:class: with the fiscal year
        containing `ref`.  If `ref` is None, use today.

        Usage::

           >>> from xoeuf.models.proxy import AccountConfigSettings
           >>> AccountConfigSettings.get_fiscal_year()
           TimeSpan('2016-10-01', '2017-09-30')
        '''
        return self.env.user.company_id.get_fiscal_year(ref)
