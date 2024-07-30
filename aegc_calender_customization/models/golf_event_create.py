from odoo import fields, models, api


class GolfEventCreate(models.Model):
    _name = 'golf.event.create'
    name = fields.Char()
    start = fields.Datetime(string="Start Date")
    end = fields.Datetime(string="End Date")
    appointment_type_id = fields.Many2one('appointment.type',string="Appointment Type",domain=[('is_visible_in_screen','=',True)])
    is_blocked = fields.Boolean(string="Is Blocked")
    date_of_event = fields.Date(compute="_compute_event_date")
    color_event = fields.Char(string="Color")

    @api.depends('start')
    def _compute_event_date(self):
        for rec in self:
            rec.date_of_event = rec.start



