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
                        absolute_import as _py3_abs_import)

import itertools
import operator

import psycopg2

from openerp.tools import mute_logger
from xoeuf import api, fields, models
from xoeuf.odoo import _, SUPERUSER_ID
from xoeuf.odoo.exceptions import Warning as UserError, except_orm as OdooError

from xoeuf.osv import savepoint
from xoeuf.osv.model_extensions import get_creator
#from openerp.jobs import DeferredType, queue

import logging
_logger = logging.getLogger(__name__)
del logging

#Deferred = DeferredType(queue=queue('partnermerge'), expires=65, retry=False)


def is_integer_list(ids):
    return all(isinstance(i, (int, long)) for i in ids)


def model_is_installed(env, model):
    proxy = env['ir.model']
    domain = [('model', '=', model)]
    return proxy.search_count(domain) > 0


class PartnerMergeInit(models.TransientModel):
    _name = 'xopgi.partner.merge.initialize'

    @api.model
    def install_fuzzy_extension(self):
        try:
            # TODO [eddy]: This is bound to fail if the user is not a
            # super-user... Check with the PostgreSQL documentation for
            # details.
            self._cr.execute('CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;')
        except Exception as error:
            _logger.error("%s", error)
            raise UserError(
                _('A required DB extension was not found. '
                  'Ask your administrator to install '
                  '"postgresql-contrib" package.')
            )


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
    wizard_id = fields.Many2one('xopgi.partner.merge.wizard', string='Wizard')
    dest_partner_id = fields.Many2one('res.partner', string='Destination partner')
    partner_ids = fields.Many2many('res.partner',
                                   rel='xopgi_partner_merge_group_partners',
                                   id1='category_id',
                                   id2='partner_id',
                                   string='Partners')

    @api.multi
    def latest_wizard(self):
        ultimo = self.env['xopgi.partner.merge.wizard'].search([])
        lasted = ultimo[-1].id
        return lasted

    name = fields.Char(
        related=('dest_partner_id', 'name'),
        string='Name',
        domain=[('wizard_id', '=', 'lasted')],
        readonly=True,
        store=True,
    )

    @api.multi
    def merge(self):
        self.ensure_one()
        self.with_context(active_test=False)._merge(self.partner_ids, self.dest_partner_id)
        self._cr.commit()  # init a new transaction
        self._check_on_alias_defaults(self.dest_partner_id,
                                      self.partner_ids)
        self._cr.commit()  # init a new transaction
        self._remove_duplicated_mail_followers(self.dest_partner_id.id)

    @mute_logger('openerp.osv.expression', 'openerp.models')
    def _merge(self, partners, dst_partner=None):
        """Merge seveal partners into just one."""
        partners = partners.exists()
        if len(partners) < 2:
            return
        merger_partner_permission = self.env.ref(
            'xopgi_object_merger.group_merger_manager'
        )
        # NOTICE that 'self.env.user' returns the user in a SUPERUSER context,
        # so don't do writes with user_groups.
        user_groups = self.env.user.mapped('groups_id')
        has_merge_permission = merger_partner_permission in user_groups
        is_superuser = self._uid == SUPERUSER_ID
        has_special_rights = is_superuser or has_merge_permission
        if not has_special_rights:
            # All user can merge up to 3 parterns with the same email, but the
            # SUPERUSER and users with 'Partner merge' can merge more than
            # that.
            if len(partners) > 3:
                raise UserError(
                    _("For safety reasons, you cannot merge more than 3 "
                      "contacts together. You can re-open the wizard several "
                      "times if needed.")
                )
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
        src_parters_has_account_move_lines = (
            not has_special_rights and
            model_is_installed(self.env, 'account.move.line') and
            self.env['account.move.line'].sudo().search(
                [('partner_id', 'in', src_partners.ids)]
            )
        )
        if src_parters_has_account_move_lines:
            raise UserError(
                _("Only the destination contact may be linked to existing "
                  "Journal Items. Please ask the Administrator if you need to "
                  "merge several contacts linked to existing Journal Items.")
            )
        self._update_foreign_keys(src_partners, dst_partner)
        self._update_reference_fields(src_partners, dst_partner)
        self._update_values(src_partners, dst_partner)
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

    def _update_foreign_keys(self, src_partners, dst_partner):
        _logger.debug(
            '_update_foreign_keys for dst_partner: %s for src_partners: %r',
            dst_partner.id, src_partners.ids

        )

        # find the many2one relation to a partner
        proxy = self.env['res.partner']
        self.get_fk_on('res_partner')

        # ignore two tables

        for table, column in self._cr.fetchall():
            if 'xopgi_partner_merge_' in table:
                continue
            partner_ids = tuple(map(int, src_partners))

            query = """SELECT column_name
                       FROM information_schema.columns
                       WHERE table_name LIKE '%s'
            """ % table
            self._cr.execute(query, ())
            columns = []
            for data in self._cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            query_dic = {
                'table': table,
                'column': column,
                'value': columns[0],
            }
            if len(columns) <= 1:
                # unique key treated
                query = """
                    UPDATE "%(table)s" as ___tu
                    SET %(column)s = %%s
                    WHERE
                        %(column)s = %%s AND
                        NOT EXISTS (
                            SELECT 1
                            FROM "%(table)s" as ___tw
                            WHERE
                                %(column)s = %%s AND
                                ___tu.%(value)s = ___tw.%(value)s
                        )""" % query_dic
                for partner_id in partner_ids:
                    self._cr.execute(
                        query,
                        (dst_partner.id, partner_id, dst_partner.id)
                    )
            else:
                try:
                    with mute_logger('openerp.sql_db'), savepoint(self._cr):
                        query = """UPDATE "%(table)s"
                                   SET %(column)s = %%s
                                   WHERE %(column)s IN %%s""" % query_dic
                        self._cr.execute(query, (dst_partner.id, partner_ids,))

                        if (column == proxy._parent_name and
                                table == 'res_partner'):
                            query = """
                                WITH RECURSIVE cycle(id, parent_id) AS (
                                        SELECT id, parent_id FROM res_partner
                                    UNION
                                        SELECT  cycle.id, res_partner.parent_id
                                        FROM    res_partner, cycle
                                        WHERE   res_partner.id = cycle.parent_id AND
                                                cycle.id != cycle.parent_id
                                )
                                SELECT id FROM cycle WHERE id = parent_id AND id = %s
                            """
                            self._cr.execute(query, (dst_partner.id,))
                except psycopg2.Error:
                    # updating fails, most likely due to a violated unique
                    # constraint keeping record with nonexistent partner_id is
                    # useless, better delete it
                    query = """DELETE FROM %(table)s
                               WHERE %(column)s = %%s""" % query_dic
                    self._cr.execute(query, (partner_id,))

    def get_fk_on(self, table):
        q = """  SELECT cl1.relname as table,
                        att1.attname as column
                   FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                        pg_attribute as att1, pg_attribute as att2
                  WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
        """
        return self._cr.execute(q, (table,))

    @api.multi
    def _update_reference_fields(self, src_partners, dst_partner):
        _logger.debug(
            '_update_reference_fields for dst_partner: %s for src_partners: %r',
            dst_partner.id, src_partners.ids

        )

        def update_records(model, src, field_model='model', field_id='res_id'):
            if model not in self.pool:
               return

            domain = [
                (field_model, '=', 'res.partner'),
                (field_id, '=', src.id)
            ]
            items = self.env[model].sudo().search(domain)
            try:
                with mute_logger('openerp.sql_db'), savepoint(self._cr):
                    return items.sudo().write({field_id: dst_partner.id})
            except psycopg2.Error:
                # updating fails, most likely due to a violated unique
                # constraint keeping record with nonexistent partner_id is
                # useless, better delete it
                return items.sudo().unlink()

        for partner in src_partners:
            update_records(
                'calendar', src=partner, field_model='model_id.model')
            update_records(
                'ir.attachment', src=partner, field_model='res_model')
            update_records(
                'mail.followers', src=partner, field_model='res_model')
            update_records('mail.message', src=partner)
            update_records(
                'marketing.campaign.workitem',
                src=partner,
                field_model='object_id.model'
            )
            update_records('ir.model.data', src=partner)

        proxy = self.env['ir.model.fields']
        domain = [('ttype', '=', 'reference')]
        records = proxy.sudo().search(domain)

        for record in records:
            try:
                proxy_model = self.env[record.model]
                column = proxy_model._columns[record.name]
            except KeyError:
                # unknown model or field => skip
                continue

            if not column and not column.store:
                continue

            for partner in src_partners:
                values = {
                    record.name: 'res.partner,%d' % dst_partner.id,
                }
                proxy_model.sudo().write(values)

    def _update_values(self, src_partners, dst_partner):
        _logger.debug(
            '_update_values for dst_partner: %s for src_partners: %r',
            dst_partner.id,
            list(map(operator.attrgetter('id'), src_partners))
        )

        columns = dst_partner._columns

        def write_serializer(column, item):
            from xoeuf.odoo.osv.orm import browse_record
            if isinstance(item, browse_record):
                return item.id
            else:
                return item

        values = dict()
        for column, field in columns.iteritems():
            if (field._type not in ('many2many', 'one2many')):
                for item in itertools.chain(src_partners, [dst_partner]):
                    if item[column]:
                        values[column] = write_serializer(column, item[column])

        values.pop('id', None)
        parent_id = values.pop('parent_id', None)
        dst_partner.write(values)
        if parent_id and parent_id != dst_partner.id:
            try:
                dst_partner.write({'parent_id': parent_id})
            except OdooError:
                _logger.info(
                    'Skip recursive partner hierarchies for parent_id %s '
                    'of partner: %s',
                    parent_id, dst_partner.id
                )

    def _check_on_alias_defaults(self, dst_partner_id, partner_ids):
        """Check if any of merged partner_ids are referenced on any mail.alias
        and on this case update the references to the dst_partner_id.
        """
        def _update_alias(i, defaults):
            Alias = self.env['mail.alias'].sudo()
            return Alias.browse(i).write({'alias_defaults': repr(defaults)})

        query = """SELECT id, alias_defaults FROM mail_alias
                     WHERE alias_model_id = {model}
                     AND (alias_defaults LIKE '%''{field}''%')"""
        self._cr.execute(
            "SELECT name, model_id, ttype FROM ir_model_fields "
            "WHERE relation='res.partner';"
        )
        read = self._cr.fetchall()
        for field, model_id, ttype in read:
            self._cr.execute(query.format(model=model_id, field=field))
            for alias_id, defaults in self._cr.fetchall():
                try:
                    defaults_dict = dict(eval(defaults))
                except Exception:
                    defaults_dict = {}
                val = defaults_dict.get(field, False)
                if not val:
                    continue
                if ttype == 'many2one':
                    if val in partner_ids and val != dst_partner_id:
                        defaults_dict[field] = dst_partner_id
                        _update_alias(alias_id, defaults_dict)
                else:
                    res_val = []
                    for rel_item in val:
                        rel_ids = rel_item[-1]
                        if isinstance(rel_ids, (tuple, list)):
                            wo_partner_ids = [i for i in rel_ids
                                              if i not in partner_ids]
                            if wo_partner_ids != rel_ids:
                                rel_ids = set(wo_partner_ids + [dst_partner_id])
                        elif rel_ids in partner_ids and val != dst_partner_id:
                            rel_ids = dst_partner_id
                        res_val.append(tuple(rel_item[:-1]) + (rel_ids,))
                    if val != res_val:
                        defaults_dict[field] = res_val
                        _update_alias(alias_id, defaults_dict)
        return True

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


class MergePartnerWizard(models.TransientModel):
    """This wizard find potential partners to merge.

    It uses to objects, the first is wizard it self for the end-user, and the
    second will contain the partner list to merge.

    """

    _name = 'xopgi.partner.merge.wizard'

    def _generate_query(self, fields, maximum_group=100):
        criteria = []
        if 'vat' in fields:
            criteria.append("""
                a.vat IS NOT NULL
                AND
                replace(lower(a.vat), ' ', '') = replace(lower(b.vat), ' ', '')
            """)

        WHERE_EMAIL_NAME = """
            position(
                metaphone(substring(a.{field}, '([^@]+)[@\s]?'), 16) in
                metaphone(substring(b.{field}, '([^@]+)[@\s]?'), 16)
            ) > 0
        """
        for text_field in ('email', 'name'):
            if text_field in fields:
                criteria.append(WHERE_EMAIL_NAME.format(field=text_field))
        if criteria:
            criteria = ' OR '.join(criteria)
            criteria = ['(%s)' % criteria]
        distance = []
        if 'name' in fields:
            distance.append("""
                levenshtein(
                    metaphone(substring(a.name, '([^@]+)@?'), 255),
                    metaphone(substring(b.name, '([^@]+)@?'), 255))
            """)
        if 'mail' in fields:
            distance.append("""
                levenshtein(
                    lower(substring(a.email, '(.+)@')),
                    lower(substring(b.email, '(.+)@')))
            """)
        if distance:
            criteria.append('least(%s, 4) <= 3' % ', '.join(distance))
        if 'parent_id' in fields:
            criteria.append('a.parent_id IS NOT NULL')
            criteria.append('a.parent_id = b.parent_id')
        if 'is_company' in fields:
            criteria.append('a.is_company AND b.is_company')
        criteria = ' AND '.join(criteria)
        query = '''SELECT a.id, array_agg(b.id)
            FROM res_partner AS a JOIN res_partner AS b ON (a.id < b.id)
            WHERE {criteria}
            GROUP BY a.id
            ORDER BY a.id
        '''.format(criteria=criteria)
        if maximum_group:
            query += "LIMIT %s" % maximum_group
        return query

    def _partner_used_in(self, aggr_ids, models):
        """True if any partner in `aggr_ids` is associated to `model`."""
        models = models or {}
        for model, field in models.iteritems():
            proxy = self.env[model]
            domain = [(field, 'in', aggr_ids)]
            if proxy.search_count(domain):
                return True
        return False

    @api.multi
    def _process_query(self, query):
        """Execute the select request and write the results."""
        proxy = self.env[('xopgi.partner.merge.group')]
        this = self[0]
        models = {}
        self._cr.execute(query)
        groups = []
        for min_id, aggr_ids in self._cr.fetchall():
            is_partner_used_in_models = self._partner_used_in(
                aggr_ids, models
            )
            if not is_partner_used_in_models:
                found_ids = set(aggr_ids + [min_id])
                for group in groups:
                    if any(found_id in group for found_id in found_ids):
                        group.update(found_ids)
                        break
                else:
                    groups.append(found_ids)
        for group in groups:
            with get_creator(proxy) as creator:
                creator.update(
                    wizard_id=this.id,
                    dest_partner_id=min(group),
                    partner_ids=group,
                )

    @api.model
    def start_process_cb(self):
        """Start the process.

        * Compute the selected groups (with duplication)

        * If the user has selected the 'exclude_XXX' fields, avoid the partners.

        """
        self.ensure_one()
        self.env['xopgi.partner.merge.group'].search([]).unlink()
        groups = ['name', 'email']
        query = self._generate_query(groups, maximum_group=100)
        self.with_context(active_test=False)._process_query(query)

#    @api.model
#    def cron_jobs_groups(self):
#        return Deferred(self.start_process_cb)
