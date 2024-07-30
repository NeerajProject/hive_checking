# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    wordpress_country_ref = fields.Char(string='Wordpress Country Reference')
