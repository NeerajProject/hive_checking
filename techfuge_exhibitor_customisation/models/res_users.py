# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    hall_ids = fields.Many2many('event.activity.location', string='Hall(s)')
    stand_ids = fields.Many2many('exhibitor.stand.details', string='Stand(s)')
    brand_id = fields.Many2one('res.brand', string='Brand')
    parent_company_id = fields.Many2one('res.partner', string='Parent Company', related='partner_id.parent_id')

    def action_reset_password(self):
        """ override to restrict sending invitation mail while creating exhibitor user """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if user.additional_email:
                email = user.additional_email
            else:
                email = user.email

            if not email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = email
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get('import_file', False))
                if not self.env.context.get('create_exhibitor_user') and not self.env.context.get(
                        'create_contractor_user'):
                    template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
                    _logger.info("Password reset email sent for user <%s> to <%s>", user.login, email)

    def action_update_exhibitor_contract_details(self):
        for user in self:
            exhibitor_contract = self.env['exhibitor.contract'].search([('exhibitor_user_id', '=', user.id)])
            if exhibitor_contract and user.partner_id.id != exhibitor_contract.partner_id.id:
                user.write({'partner_id': exhibitor_contract.partner_id.id})
