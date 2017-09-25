#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# base_partner_merge
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-03-30

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_impor)

from openerp.tools import mute_logger
from xoeuf import api, fields, models
from xoeuf.odoo import _
from xoeuf.odoo.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)
del logging


def model_is_installed(env, model):
    proxy = env['ir.model']
    domain = [('model', '=', model)]
    return proxy.search_count(domain) > 0


class ResPartner(models.Model):
    _inherit = 'res.partner'

    id = fields.Integer('Id', readonly=True)
    create_date = fields.Datetime('Create Date', readonly=True)


class MergePartnerGroup(models.TransientModel):
    """Represent a partner o a parter group.

    - Is a partner when `parent_id` points to another instance of the same
      type representing the group.

    - Is a group when has no `parent_id`  and several partners point to here.
      In this case the referenced partner is the destination partner.

    """
    _name = 'xopgi.partner.merge.group'
    _order = "name asc"
    dest_partner_id = fields.Many2one('res.partner', string='Destination partner')
    partner_ids = fields.Many2many('res.partner',
                                   rel='xopgi_partner_merge_group_partners',
                                   id1='category_id',
                                   id2='partner_id',
                                   string='Partners')

    name = fields.Char(
        related=('dest_partner_id', 'name'),
        string='Name',
        readonly=True,
        store=True,
    )

    @api.multi
    def merge(self):
        self.ensure_one()
        self.with_context(active_test=False)._merge(self.partner_ids, self.dest_partner_id)
        self._cr.commit()  # init a new transaction
        self._remove_duplicated_mail_followers(self.dest_partner_id.id)
        self.unlink()

    @mute_logger('openerp.osv.expression', 'openerp.models')
    def _merge(self, partners, dst_partner=None):
        """Merge seveal partners into just one."""
        partners = partners.exists()
        if len(partners) < 2:
            return
        partner_different_emails = {
                p.email
                for p in partners
                if p.email and p.email.strip()
        }
        if len(partner_different_emails) > 1:
                raise UserError(
                    _("All contacts must have the same email. Only the "
                      "users with Partner Merge rights can merge contacts "
                      "with different emails.")
                )
        if not dst_partner:
            partners = self._get_ordered_partner(partners)
            dst_partner = partners[-1]
        src_partners = partners - dst_partner
        _logger.info("dst_partner: %s", dst_partner.id)
        merger = self.env['object.merger']
        active_model = 'res.partner'
        merger._merge(active_model, dst_partner.id, src_partners.ids)
        self._cr.commit()
        merger._check_on_alias_defaults(dst_partner.id, src_partners.ids, active_model)
        _logger.info(
            '(uid = %s) merged the partners %r with %s',
            self._uid, src_partners.ids,
            dst_partner.id
        )
        name_emails = [(p.name, p.email or 'n/a', p.id) for p in src_partners]
        name_emails = ', '.join('%s<%s>(ID %s)' % name for name in name_emails)
        dst_partner.message_post(
            body='%s %s' % (
                _("Merged with the following partners:"),
                name_emails
            )
        )
        for partner in src_partners:
            partner.unlink()

    def _get_ordered_partner(self, partners):

        ordered_partners = partners.sorted(
            key=lambda partner: (partner.create_date, partner.active),
            reverse=True
        )
        return ordered_partners

    def _remove_duplicated_mail_followers(self, dst_partner_id):
        """Delete all duplicated mail_followers with
        partner_id = dst_partner_id and create one by each group.
        """
        select_query = """
          SELECT res_id, res_model, partner_id
          FROM (SELECT COUNT(id) quantity, res_id, res_model, partner_id
                FROM mail_followers WHERE partner_id = %s
                GROUP BY res_id, res_model, partner_id) grouped_table
          WHERE quantity>1"""
        self._cr.execute(select_query % dst_partner_id)
        read = self._cr.fetchall()
        if not read:
            return True
        del_query = """
          DELETE FROM mail_followers
          WHERE res_id={res_id} AND res_model='{res_model}' AND partner_id={partner_id}
          """
        insert_query = """
          INSERT INTO mail_followers(res_id, res_model, partner_id)
          VALUES ({res_id}, '{res_model}', {partner_id})
        """
        for res_id, res_model, partner_id in read:
            self._cr.execute(del_query.format(res_id=res_id, res_model=res_model,
                                              partner_id=dst_partner_id))
            self._cr.execute(insert_query.format(res_id=res_id, res_model=res_model,
                                                 partner_id=dst_partner_id))
        return True
