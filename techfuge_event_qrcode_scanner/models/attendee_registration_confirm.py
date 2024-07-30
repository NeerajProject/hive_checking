# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AttendeeRegistrationConfirm(models.Model):
    _name = 'attendee.registration.confirm'
    _description = 'Attendee Registration Confirm'

    attendee_id = fields.Many2one('event.registration', string="Attendee")
    name = fields.Char(string="Name")
    designation = fields.Char(string="Designation")
    company_name = fields.Char(string="Company Name")
    event_id = fields.Many2one('event.event', string="Event")
    hall_id = fields.Many2one("event.activity.location", string="Hall")
    location_name = fields.Char(string="Location")
    exhibitor_name = fields.Char(string="Exhibitor Name")
    stand_number = fields.Char(string="Stand Number")

    @api.model
    def create_attendee_registration_data(self, attendee_id):
        vals = {}
        user = self.env.user
        attendee_registration_id = False
        if attendee_id:
            attendee = self.env['event.registration'].browse(int(attendee_id))

            if attendee:
                vals.update({
                    'attendee_id': attendee.id,
                    'name': attendee.attendee_full_name,
                    'designation': attendee.designation,
                    'company_name': attendee.company_name,
                    'event_id': attendee.event_id.id,
                    'exhibitor_name': attendee.exhibitor_name
                })

                if user.hall_ids:
                    vals.update({
                        'hall_id': user.hall_ids.id,
                        'location_name': user.hall_ids.name,
                    })

                if user.stand_ids:
                    vals.update({
                        'stand_number': user.stand_ids.stand_number
                    })

                attendee_registration_id = self.env['attendee.registration.confirm'].create(vals).id

        return attendee_registration_id

    @api.model
    def confirm_attendee_registration(self, record_id):
        menu_id = False
        if record_id:
            record = self.sudo().browse(int(record_id))
            if record:
                if record.attendee_id and record.location_name and record.stand_number:
                    activity_id = self.env['event.attendee.activities'].create({
                        'attendee_id': record.attendee_id.id,
                        'event_id': record.event_id.id,
                        'name': record.location_name,
                        'activity_location_type_id': record.hall_id.activity_location_type_id.id,
                        'user_id': self.env.user.id,
                        'exhibitor_name': record.exhibitor_name,
                        'stand_number': record.stand_number,
                        'attendee_activity_datetime': fields.Datetime.now()
                    })

                    if activity_id:
                        menu_id = self.env.ref('techfuge_event_qrcode_scanner.event_qr_code_scanner').id
        return menu_id

    @api.model
    def print_attendee_badge(self, record_id):
        record = self.sudo().browse(int(record_id))
        badge_attachment_id = False
        if record:
            if record.attendee_id and record.attendee_id.badge_attachment_id:
                badge_attachment_id = record.attendee_id.badge_attachment_id.id
        return badge_attachment_id
