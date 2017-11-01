#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# test_merge_group
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-13


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_impor)


from xoeuf.odoo.tests.common import TransactionCase


class TestPartnergroup(TransactionCase):
    def setUp(self):
        super(TestPartnergroup, self).setUp()
        partner = self.env['res.partner']
        partner_group = self.env['xopgi.partner.merge.group']
        self.partner_group = self.env['xopgi.partner.merge.group']
        self.partner1 = partner.create(
            dict(name='erich', email='erich@company.com'))
        self.partner2 = partner.create(
            dict(name='erick', email='erich@company.com'))
        self.partner3 = partner.create(
            dict(name='eric', email='erich@company.com'))

        self.group1 = partner_group.create(dict(dest_partner_id=self.partner1.id))

        self.group1.partner_ids += self.partner1
        self.group1.partner_ids += self.partner2
        self.group1.partner_ids += self.partner3

    def test_check_group(self):
        sources = self.group1.partner_ids
        # check that only the three objects that make up the group are merge
        self.assertEqual(len(sources), 3)
        self.group1.merge()
        group = self.partner_group.search([('dest_partner_id', '=', self.partner1.id)])
        self.assertFalse(group)
