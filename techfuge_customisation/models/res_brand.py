# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Brand(models.Model):
    _name = 'res.brand'
    _description = 'Brand'

    name = fields.Char(string='Name')
