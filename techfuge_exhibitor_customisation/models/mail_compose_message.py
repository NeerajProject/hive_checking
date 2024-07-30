from odoo import models,fields,api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_unsent_confirm(self):
            self.email_from = 'no_need_to_sent_email'
            return super().action_send_mail()






