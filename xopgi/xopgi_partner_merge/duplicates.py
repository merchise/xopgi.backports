#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Detect possible duplicate partners.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_impor)


from xoeuf import api, models
from xoeuf.odoo import _
from xoeuf.odoo.exceptions import Warning as UserError
from xoeuf.odoo.jobs import Deferred, until_timeout
from xoeuf.models.extensions import get_creator

import logging
_logger = logging.getLogger(__name__)
del logging


def model_is_installed(env, model):
    proxy = env['ir.model']
    domain = [('model', '=', model)]
    return proxy.search_count(domain) > 0


class PartnerMergeInit(models.TransientModel):
    _name = 'xopgi.partner.merge.initialize'

    @api.model
    def install_fuzzy_extension(self):
        try:
            # TODO: This is bound to fail if the user is not a
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


class MergePartnerWizard(models.TransientModel):
    """This wizard find potential partners to merge.
    """
    _name = 'xopgi.partner.merge.wizard'

    @api.multi
    def _process_query(self):
        """Execute the select query."""
        query = '''SELECT b.id
            FROM res_partner AS a JOIN res_partner AS b ON (a.id < b.id)
            WHERE (
            position(
                metaphone(substring(a.email, '([^@]+)[@\s]?'), 16) in
                metaphone(substring(b.email, '([^@]+)[@\s]?'), 16)
            ) > 0
        ) AND levenshtein(
                    metaphone(substring(a.name, '([^@]+)@?'), 255),
                    metaphone(substring(b.name, '([^@]+)@?'), 255)) <= 3
          AND a.id = {id} and b.active is True'''
        partners = self.env['res.partner'].search([], order='id')
        todo = partners.ids
        while todo:
            id = todo.pop(0)
            self._cr.execute(query.format(id=id))
            query_res = self._cr.fetchall()
            for dst_id, in query_res:
                if dst_id in todo:
                    todo.remove(dst_id)
            yield id, query_res

    @api.model
    def generate_duplicate(self):
        """Compute the selected groups (with duplication)
        """
        proxy = self.env[('xopgi.partner.merge.group')]
        for partner_id, others in until_timeout(self._process_query()):
            partner_groups = proxy.search([('dest_partner_id', '=', partner_id)])
            if others and not partner_groups:
                with get_creator(proxy) as creator:
                    creator.update(
                        dest_partner_id=partner_id,
                        partner_ids=[partner_id] + others
                    )

    @api.model
    def start_process_duplicate(self):
        '''Use celery and create the groups .
        '''
        return Deferred(self.generate_duplicate)
