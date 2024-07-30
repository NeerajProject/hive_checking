# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventActivityLocation(models.Model):
    _name = 'event.activity.location'
    _description = 'Event Activity Location'

    name = fields.Char(string='Location')
    event_id = fields.Many2one('event.event', string='Event')
    activity_location_type_id = fields.Many2one('activity.location.type', string='Type')
    activity_location_group = fields.Char(string='Group')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Hall already exists !"),
    ]

    @api.onchange('activity_location_type_id')
    def onchange_activity_location_type_id(self):
        if self.activity_location_type_id:
            self.activity_location_group = self.activity_location_type_id.attendee_group_id.name


class EventAttendeeActivities(models.Model):
    _name = 'event.attendee.activities'
    _description = 'Event Attendee Activities'
    name = fields.Char(string='Location')
    attendee_id = fields.Many2one('event.registration', string='Attendee', ondelete='cascade')
    barcode = fields.Char(related="attendee_id.attendee_reg_no")

    attendee_full_name = fields.Char(string="Attendee Name", related="attendee_id.attendee_full_name")
    attendee_ref_id = fields.Integer(string="Attendee ID", related='attendee_id.id')
    attendee_company_name = fields.Char(string="Company Name", related="attendee_id.company_name")
    attendee_designation = fields.Char(string="Designation", related="attendee_id.designation")
    country_id = fields.Many2one('res.country', string='Country', related="attendee_id.country_id")
    event_id = fields.Many2one('event.event', string='Event')
    event_reference = fields.Char(string='Event Reference No.', related='event_id.event_ref_no')
    activity_location_type_id = fields.Many2one('activity.location.type', string='Type')
    attendee_type_id = fields.Many2one('event.attendee.type',related="attendee_id.attendee_type_id",store=True)
    attendee_activity_group = fields.Char(string='Group')
    user_id = fields.Many2one('res.users', string='User')
    exhibitor_name = fields.Char(string='Exhibitor')
    stand_number = fields.Char(string='Stand Number')
    attendee_activity_datetime = fields.Datetime(string='Date & Time')
