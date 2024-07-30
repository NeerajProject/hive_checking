
from odoo import api, fields, models
from odoo import Command


class Event(models.Model):
    _inherit = 'event.event'

    exhibitor_email_template_id = fields.Many2one('mail.template',string="Exhibitor Email Template", domain=[('model', '=', 'sale.order'),('is_exihibitor_mail','=',True)] )
    # exhibitor_country_agreement_ids = fields.Many2many('event.agreement.country',string="Exhibitor Agreement Template")
