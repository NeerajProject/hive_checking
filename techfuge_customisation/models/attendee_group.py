# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventAttendeeGroup(models.Model):
    _name = 'event.attendee.group'
    _description = 'Event Attendee Group'

    name = fields.Char(string='Name')
