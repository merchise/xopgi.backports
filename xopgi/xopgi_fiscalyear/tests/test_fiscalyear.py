#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# test_fiscalyear
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-20

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from datetime import date
from hypothesis import given, strategies as s
from xoeuf.odoo.tests.common import TransactionCase


class TestFiscalYear(TransactionCase):
    @given(s.dates(min_value=date(2000, 1, 1)))
    def test_get_fiscal_year(self, ref):
        company = self.env.user.company_id
        assert ref in company.get_fiscal_year(ref)
        assert company.get_fiscal_year(ref).valid

    def test_currenct_fiscal_year(self):
        today = date.today()
        assert today in self.env['account.config.settings'].get_fiscal_year()
