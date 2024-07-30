# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventVisitPurpose(models.Model):
    _name = 'event.visit.purpose'
    _description = 'Event Visit Purpose'

    name = fields.Char(string='Name')
