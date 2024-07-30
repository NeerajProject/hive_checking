# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorSpaceType(models.Model):
    _name = 'exhibitor.space.type'
    _description = 'Exhibitor Space Type'

    name = fields.Char(string="Name")
    type = fields.Selection([
        ('package', 'Package'), ('non-package', 'Non-Package')
    ], string='Type')
