# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventAttendeeType(models.Model):
    _name = 'event.attendee.type'
    _description = 'Event Attendee Type'

    name = fields.Char(string='Name')
    type = fields.Selection(selection=[
        ('exhibitor', 'Exhibitor'),
        ('visitor', 'Visitor'),
        ('vip_visitor', 'VIP Visitor'),
        ('contractor', 'Contractor'),
        ('organizer', 'Organizer'),
    ], string='Type')
    attendee_group_id = fields.Many2one('event.attendee.group', string='Group')
    badge_mail_template_id = fields.Many2one('mail.template', string='Mail Template',
                                             help='Email template to send badge')
