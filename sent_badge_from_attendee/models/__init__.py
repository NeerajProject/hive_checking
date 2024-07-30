from odoo import api, fields, models, _

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def cron_badge_sent(self):
        record = self.env['event.registration'].search([('badge_sent','=',False)],limit=50)
        for rec in record:
           rec.action_send_visitor_badge_mail()