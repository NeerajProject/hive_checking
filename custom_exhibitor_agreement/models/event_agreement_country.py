from odoo import fields, models, api


class EventAgreementCountry(models.Model):
    _name = 'event.agreement.country'

    name = fields.Char()
    event_id = fields.Many2one('event.event')
    email_template_id = fields.Many2one('mail.template')
    country_id = fields.Many2one('res.country')
    payment_instruction = fields.Text(string="Payment Instruction")
    special_instruction = fields.Text(string="Special Instruction")

    different_payment_description = fields.Boolean(default='False')