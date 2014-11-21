#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print)


import functools
import itertools
import logging
import operator
import psycopg2
from ast import literal_eval
from openerp.tools import mute_logger

import openerp
from openerp.osv import osv, orm
from openerp.osv import fields
from openerp.osv.orm import browse_record
from openerp.tools.translate import _

from xoeuf.osv import savepoint

_logger = logging.getLogger('base.partner.merge')


def is_integer_list(ids):
    return all(isinstance(i, (int, long)) for i in ids)


class PartnerMergeInit(osv.TransientModel):
    _name = str('base.partner.merge.initialize')

    def install_fuzzy_extension(self, cr, uid, context=None):
        try:
            cr.execute('CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;')
        except:
            raise osv.Error(_('DB Server Error'),
                            _('A required DB extension was not found. '
                              'Ask your administrator to install '
                              '"postgresql-contrib" package.'))


class ResPartner(osv.Model):
    _inherit = str('res.partner')

    _columns = {
        'id': fields.integer('Id', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
    }


class MergePartnerLine(osv.TransientModel):
    _name = str('base.partner.merge.line')

    _columns = {
        'wizard_id': fields.many2one('base.partner.merge.wizard',
                                     'Wizard'),
        'min_id': fields.integer('MinID'),
        'aggr_ids': fields.char('Ids', required=True),
    }

    _order = 'min_id asc'


class MergePartner(osv.TransientModel):
    """This wizard find potential partners to merge.

    It uses to objects, the first is wizard it self for the end-user, and the
    second will contain the partner list to merge.

    """

    _name = str('base.partner.merge.wizard')

    _columns = {
        # Group by
        'filter_by_name': fields.char('Name', required=False),
        'group_by_email': fields.boolean('Email'),
        'group_by_name': fields.boolean('Name'),
        'group_by_is_company': fields.boolean('Is Company'),
        'group_by_vat': fields.boolean('VAT'),
        'group_by_parent_id': fields.boolean('Parent Company'),

        'number_group':
            fields.integer("Group of Contacts", readonly=True),
        'current_line_id':
            fields.many2one('base.partner.merge.line', 'Current Line'),
        'line_ids':
            fields.one2many('base.partner.merge.line', 'wizard_id', 'Lines'),
        'partner_ids':
            fields.many2many('res.partner', string='Contacts'),
        'dst_partner_id':
            fields.many2one('res.partner', string='Destination Contact'),

        'exclude_contact':
            fields.boolean('A user associated to the contact'),
        'exclude_journal_item':
            fields.boolean('Journal Items associated to the contact'),
        'maximum_group':
            fields.integer("Maximum of Group of Contacts"),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(MergePartner, self).default_get(
            cr, uid, fields, context
        )
        if (context.get('active_model') == 'res.partner'
                and context.get('active_ids')):
            partner_ids = context['active_ids']
            res['partner_ids'] = partner_ids
            res['dst_partner_id'] = self._get_ordered_partner(
                cr, uid, partner_ids, context=context
            )[-1].id
        return res

    _defaults = {
        'group_by_name': True,
        'group_by_email': True,
    }

    def get_fk_on(self, cr, table):
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
        return cr.execute(q, (table,))

    def _update_foreign_keys(self, cr, uid, src_partners, dst_partner,
                             context=None):
        _logger.debug(
            '_update_foreign_keys for dst_partner: %s for src_partners: %r',
            dst_partner.id,
            list(map(operator.attrgetter('id'), src_partners))
        )

        # find the many2one relation to a partner
        proxy = self.pool.get('res.partner')
        self.get_fk_on(cr, 'res_partner')

        # ignore two tables

        for table, column in cr.fetchall():
            if 'base_partner_merge_' in table:
                continue
            partner_ids = tuple(map(int, src_partners))

            query = """SELECT column_name
                       FROM information_schema.columns
                       WHERE table_name LIKE '%s'
            """ % table
            cr.execute(query, ())
            columns = []
            for data in cr.fetchall():
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
                    cr.execute(
                        query,
                        (dst_partner.id, partner_id, dst_partner.id)
                    )
            else:
                try:
                    with mute_logger('openerp.sql_db'), savepoint(cr):
                        query = """UPDATE "%(table)s"
                                   SET %(column)s = %%s
                                   WHERE %(column)s IN %%s""" % query_dic
                        cr.execute(query, (dst_partner.id, partner_ids,))

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
                            cr.execute(query, (dst_partner.id,))
                except psycopg2.Error:
                    # updating fails, most likely due to a violated unique
                    # constraint keeping record with nonexistent partner_id is
                    # useless, better delete it
                    query = """DELETE FROM %(table)s
                               WHERE %(column)s = %%s""" % query_dic
                    cr.execute(query, (partner_id,))

    def _update_reference_fields(self, cr, uid, src_partners, dst_partner,
                                 context=None):
        _logger.debug(
            '_update_reference_fields for dst_partner: %s for src_partners: %r',
            dst_partner.id,
            list(map(operator.attrgetter('id'), src_partners))
        )

        def update_records(model, src, field_model='model', field_id='res_id',
                           context=None):
            proxy = self.pool.get(model)
            if proxy is None:
                return
            domain = [
                (field_model, '=', 'res.partner'),
                (field_id, '=', src.id)
            ]
            ids = proxy.search(
                cr, openerp.SUPERUSER_ID, domain, context=context)
            try:
                with mute_logger('openerp.sql_db'), savepoint(cr):
                    return proxy.write(
                        cr, openerp.SUPERUSER_ID, ids,
                        {field_id: dst_partner.id},
                        context=context
                    )
            except psycopg2.Error:
                # updating fails, most likely due to a violated unique
                # constraint keeping record with nonexistent partner_id is
                # useless, better delete it
                return proxy.unlink(
                    cr, openerp.SUPERUSER_ID, ids, context=context
                )

        update_records = functools.partial(update_records, context=context)

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

        proxy = self.pool['ir.model.fields']
        domain = [('ttype', '=', 'reference')]
        record_ids = proxy.search(
            cr, openerp.SUPERUSER_ID, domain, context=context)

        records = proxy.browse(
            cr, openerp.SUPERUSER_ID, record_ids, context=context
        )
        for record in records:
            try:
                proxy_model = self.pool[record.model]
                field_type = proxy_model._columns[record.name].__class__._type
            except KeyError:
                # unknown model or field => skip
                continue

            if field_type == 'function':
                continue

            for partner in src_partners:
                domain = [
                    (record.name, '=', 'res.partner,%d' % partner.id)
                ]
                model_ids = proxy_model.search(
                    cr, openerp.SUPERUSER_ID, domain, context=context
                )
                values = {
                    record.name: 'res.partner,%d' % dst_partner.id,
                }
                proxy_model.write(
                    cr, openerp.SUPERUSER_ID, model_ids, values,
                    context=context
                )

    def _update_values(self, cr, uid, src_partners, dst_partner, context=None):
        _logger.debug(
            '_update_values for dst_partner: %s for src_partners: %r',
            dst_partner.id,
            list(map(operator.attrgetter('id'), src_partners))
        )

        columns = dst_partner._columns

        def write_serializer(column, item):
            if isinstance(item, browse_record):
                return item.id
            else:
                return item

        values = dict()
        for column, field in columns.iteritems():
            if (field._type not in ('many2many', 'one2many') and
                    not isinstance(field, fields.function)):
                for item in itertools.chain(src_partners, [dst_partner]):
                    if item[column]:
                        values[column] = write_serializer(column, item[column])

        values.pop('id', None)
        parent_id = values.pop('parent_id', None)
        dst_partner.write(values)
        if parent_id and parent_id != dst_partner.id:
            try:
                dst_partner.write({'parent_id': parent_id})
            except (osv.except_osv, orm.except_orm):
                _logger.info(
                    'Skip recursive partner hierarchies for parent_id %s '
                    'of partner: %s',
                    parent_id, dst_partner.id
                )

    @mute_logger('openerp.osv.expression', 'openerp.models')
    def _merge(self, cr, uid, partner_ids, dst_partner=None, context=None):
        proxy = self.pool.get('res.partner')

        partner_ids = proxy.exists(cr, uid, list(partner_ids), context=context)
        if len(partner_ids) < 2:
            return

        is_superuser = uid == openerp.SUPERUSER_ID

        if not is_superuser:
            if len(partner_ids) > 3:
                raise osv.except_osv(
                    _('Error'),
                    _("For safety reasons, you cannot merge more than 3 "
                      "contacts together. You can re-open the wizard several "
                      "times if needed.")
                )

            partners = proxy.browse(cr, uid, partner_ids, context=context)
            if len(set(p.email for p in partners)) > 1:
                raise osv.except_osv(
                    _('Error'),
                    _("All contacts must have the same email. Only the "
                      "Administrator can merge contacts with different emails.")
                )

        if dst_partner and dst_partner.id in partner_ids:
            src_partners = proxy.browse(
                cr, uid,
                [id for id in partner_ids if id != dst_partner.id],
                context=context
            )
        else:
            ordered_partners = self._get_ordered_partner(
                cr, uid, partner_ids, context)
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]
        _logger.info("dst_partner: %s", dst_partner.id)

        src_parters_has_account_move_lines = (
            not is_superuser and
            self._model_is_installed(
                cr, uid, 'account.move.line', context=context) and
            self.pool.get('account.move.line').search(
                cr, openerp.SUPERUSER_ID,
                [('partner_id', 'in', [p.id for p in src_partners])],
                context=context)
        )
        if src_parters_has_account_move_lines:
            raise osv.except_osv(
                _('Error'),
                _("Only the destination contact may be linked to existing "
                  "Journal Items. Please ask the Administrator if you need to "
                  "merge several contacts linked to existing Journal Items.")
            )

        call_it = lambda function: function(cr, uid, src_partners, dst_partner,
                                            context=context)

        call_it(self._update_foreign_keys)
        call_it(self._update_reference_fields)
        call_it(self._update_values)

        _logger.info(
            '(uid = %s) merged the partners %r with %s',
            uid,
            list(map(operator.attrgetter('id'), src_partners)),
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

    def close_cb(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def _generate_query(self, fields, name=None, maximum_group=100):
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

        if name:
            criteria.append("a.name ILIKE '%{name}%'".format(name=name))

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

    def _compute_selected_groupby(self, this):
        group_by_str = 'group_by_'
        group_by_len = len(group_by_str)

        fields = [
            key[group_by_len:]
            for key in self._columns.keys()
            if key.startswith(group_by_str)
        ]

        groups = [
            field
            for field in fields
            if getattr(this, '%s%s' % (group_by_str, field), False)
        ]

        if this.filter_by_name and 'name' not in groups:
            groups.append('name')

        if not groups:
            raise osv.except_osv(
                _('Error'),
                _("You have to specify a filter for your selection")
            )

        return groups

    def _get_ordered_partner(self, cr, uid, partner_ids, context=None):
        partners = self.pool.get('res.partner').browse(
            cr, uid, list(partner_ids), context=context
        )
        ordered_partners = sorted(
            partners,
            key=lambda partner: (partner.create_date, partner.active),
            reverse=True
        )
        return ordered_partners

    def _next_screen(self, cr, uid, this, context=None):
        this.refresh()
        values = {}
        if this.line_ids:
            # in this case, we try to find the next record.
            current_line = this.line_ids[0]
            current_partner_ids = literal_eval(current_line.aggr_ids)
            values.update({
                'current_line_id': current_line.id,
                'partner_ids': [(6, 0, current_partner_ids)],
                'dst_partner_id': self._get_ordered_partner(
                    cr, uid, current_partner_ids, context)[-1].id,
            })
        else:
            values.update({
                'current_line_id': False,
                'partner_ids': [],
            })

        this.write(values)

        return {
            'type': 'ir.actions.act_window',
            'res_model': this._name,
            'res_id': this.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _model_is_installed(self, cr, uid, model, context=None):
        proxy = self.pool.get('ir.model')
        domain = [('model', '=', model)]
        return proxy.search_count(cr, uid, domain, context=context) > 0

    def _partner_used_in(self, cr, uid, aggr_ids, models, context=None):
        """True if any partner in `aggr_ids` is associated to `model`."""
        models = models or {}
        for model, field in models.iteritems():
            proxy = self.pool.get(model)
            domain = [(field, 'in', aggr_ids)]
            if proxy.search_count(cr, uid, domain, context=context):
                return True
        return False

    def compute_models(self, cr, uid, ids, context=None):
        """Return the model -> field associated to partner.

        If you want to exclude certain partners from the search this method
        returns the information needed for the exclusion system.
        """
        assert is_integer_list(ids)

        this = self.browse(cr, uid, ids[0], context=context)

        models = {}
        if this.exclude_contact:
            models['res.users'] = 'partner_id'

        account_move_line_is_installed = self._model_is_installed(
            cr, uid, 'account.move.line', context=context
        )
        if this.exclude_journal_item and account_move_line_is_installed:
            models['account.move.line'] = 'partner_id'

        return models

    def _process_query(self, cr, uid, ids, query, context=None):
        """Execute the select request and write the results."""
        proxy = self.pool.get('base.partner.merge.line')
        this = self.browse(cr, uid, ids[0], context=context)
        models = self.compute_models(cr, uid, ids, context=context)
        cr.execute(query)

        groups = []
        for min_id, aggr_ids in cr.fetchall():
            is_partner_used_in_models = self._partner_used_in(
                cr, uid, aggr_ids, models, context=context
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
            values = {
                'wizard_id': this.id,
                'min_id': min(group),
                'aggr_ids': sorted(group),
            }
            proxy.create(cr, uid, values, context=context)

        counter = len(groups)

        values = {
            'number_group': counter,
        }

        this.write(values)

        _logger.info("counter: %s", counter)

    def start_process_cb(self, cr, uid, ids, context=None):
        """Start the process.

        * Compute the selected groups (with duplication)
        * If the user has selected the 'exclude_XXX' fields, avoid the partners.

        """
        assert is_integer_list(ids)

        context = dict(context or {}, active_test=False)
        this = self.browse(cr, uid, ids[0], context=context)
        groups = self._compute_selected_groupby(this)
        query = self._generate_query(
            groups,
            name=this.filter_by_name,
            maximum_group=this.maximum_group,
        )
        self._process_query(cr, uid, ids, query, context=context)

        return self._next_screen(cr, uid, this, context)
