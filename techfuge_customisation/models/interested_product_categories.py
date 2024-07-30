# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InterestedProductCategories(models.Model):
    _name = 'interested.product.categories'
    _description = 'Interested Product Categories'

    name = fields.Char(string='Name')
