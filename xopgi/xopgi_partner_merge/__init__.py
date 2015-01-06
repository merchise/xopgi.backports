from openerp.release import version_info

if version_info < (8, 0):
    from . import base_partner_merge  # noqa
