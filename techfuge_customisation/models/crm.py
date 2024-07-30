# -*- coding: utf-8 -*-

from odoo import api, fields, models
import random


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    title_abbr = fields.Selection(selection=[
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ], string='Title Abbreviation')
    last_name = fields.Char(string="Last Name")
    partner_full_name = fields.Char(string="Partner Full Name")
    product_categories = fields.Selection(selection=[
        ('Furniture', 'Furniture'),
        ('Home Decor/Textiles', 'Home Decor/Textiles'),
    ], string='Product Category')
    about_exhibitor_company = fields.Text(string="About Company")
    communication_permission = fields.Boolean(string="Communication Permission", default=False)
    fax_no = fields.Char(string="Fax")
    reference_id = fields.Many2one('res.partner', string="Reference")
    brand_id = fields.Many2one('res.brand', string='Brand')
    year = fields.Char(string='Year')
    exhibitor_user_id = fields.Many2one('res.users', string='Exhibitor User')
    exhibitor_user_login = fields.Char(string='Exhibitor User Login')
    exhibitor_user_password = fields.Char(string='Exhibitor User Password')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
