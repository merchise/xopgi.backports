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

from xoeuf.odoo.tests.common import TransactionCase
from xoeuf.osv.orm import REPLACEWITH_RELATED as REPLACEWITH


class TestAccessRight(TransactionCase):
    """Tests for permissions to users to 'product price type' field."""
    def setUp(self):
        super(TestAccessRight, self).setUp()
        User = self.env['res.users']
        main_company = self.env.ref('base.main_company')
        res_user_group = self.env.ref('base.group_user')
        self.product_price_type1 = self.env.ref('product.list_price')
        self.base_user = User.with_context({'no_reset_password': True}).create(dict(
            name="User",
            company_id=main_company.id,
            login="user",
            email="user@yourcompany.com",
            groups_id=[
                REPLACEWITH(res_user_group.id,)
            ]
        ))

    def test_user_access_rights_to_pricelist_type(self):
        """Test an user with 'basic' permission which have rights to read pricelist
        type field.

        """
        self.product_price_type1.sudo(self.base_user).read()
