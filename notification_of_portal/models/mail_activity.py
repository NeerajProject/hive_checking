from odoo import models,fields,api


class MailActivity(models.Model):
    _inherit = "mail.activity"

    company_name = fields.Char(string="Company Name")
    section = fields.Char(string="Section")
    is_portal_activity = fields.Boolean()
    event_id = fields.Many2one('event.event',related='user_id.event_id', string="Event")
