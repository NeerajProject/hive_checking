# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SpecialInclusionInfo(models.Model):
    _name = 'special.inclusion.info'
    _description = 'Special Inclusion Info'

    name = fields.Char(string='Name')
    description = fields.Html(string='Description', translate=True, prefetch=True, sanitize=False)
