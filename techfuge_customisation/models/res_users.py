# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    event_id = fields.Many2one("event.event", string="Event")
    user_category = fields.Selection(selection=[
        ('exhibitor', 'Exhibitor'),
        ('contractor', 'Contractor'),
    ], string="User Category")
