#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import fields, models


class ProjectTaskStage(models.Model):
    """ Override project.task.type model to add a 'closed' boolean field allowing
        to know that tasks in this stage are considered as closed. """
    _name = 'project.task.type'
    _inherit = 'project.task.type'

    closed = fields.Boolean(
        'Close',
        help="Tasks in this stage are considered as closed.",
        default=False
    )
