from odoo import api, fields, models, _

class ExhibitorContractorDetails(models.Model):
    _inherit = 'exhibitor.contractor.details'

    def grant_portal_access_for_contractor(self):
        res_users = self.env['res.users'].sudo()
        user_password = self.generate_random_password()

        if not res_users.search([('login', '=', self.email)]):
            if self.contractor_full_name and self.email:
                contractor_user = res_users.with_context(create_contractor_user=True).create({
                    'name': self.contractor_full_name,
                    'mobile': self.mobile,
                    'email': self.email,
                    'login': self.email,
                    'password': user_password,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                    'partner_id': self.partner_id.id,
                    'user_category': 'contractor',
                    'event_id': self.event_id.id,
                    'brand_id': self.brand_id.id if self.brand_id else False
                })
                self.exhibitor_user_id = contractor_user.id
                self.sudo().write({
                    'contractor_user_id': contractor_user.id,
                    'contractor_user_login': contractor_user.login,
                    'contractor_user_password': user_password,
                })


                if self.event_id.event_contractor_registration:
                    user = self.env.ref('base.user_admin')
                    mail_template = self.event_id.event_contractor_registration
                    mail_template.with_user(user.id).sudo().with_context(
                        contractor_full_name=self.contractor_full_name).send_mail(
                        self.id, force_send=True
                    )

                    self.status = 'access_granted'