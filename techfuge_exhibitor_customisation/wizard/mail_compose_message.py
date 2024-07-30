# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _action_send_mail(self, auto_commit=False):
        if self.model == 'sale.order':
            context = self.env.context
            if context.get('is_exhibitor_agreement'):
                sale_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
                if not context.get('is_called_from_action'):
                    sale_id.sudo().write({
                        'agreement_sent': True
                    })
                    sale_id.generate_exhibitor_contract()
        return super(MailComposeMessage, self)._action_send_mail(auto_commit=auto_commit)
