# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventBusinessNature(models.Model):
    _name = 'event.business.nature'
    _description = 'Event Attendee Group'

    name = fields.Char(string='Name')
