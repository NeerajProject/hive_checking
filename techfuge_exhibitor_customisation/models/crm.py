# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    sent_registration_mails = fields.Boolean(string="Sent Registration Mail", default=False)
    agent_id = fields.Many2one("res.partner", string="Agent", domain=[('is_agent', '=', True)])
    source_of_registration = fields.Selection(selection=[
        ('from_website', 'Website Registration'),
        ('onsite_registration', 'Onsite Registration'),
        ('excel_upload', 'Excel Upload'),
    ], string='Source of Registration', default='onsite_registration')
    sale_order_state = fields.Char(string="Order Status", compute="_compute_sale_order_state")
    additional_email = fields.Char(string="Customer Email")
    desired_area_in_sqm = fields.Char(string="Desired Area in SQM ",tracking=True)
    is_duplicate = fields.Boolean()
    def send_exhibitor_registration_mail_to_exhibitor(self):
        user = self.env.ref('base.user_admin')
        if self.event_id:
            mail_template = self.event_id.exhibitor_registeration_template
        else:
            mail_template = self.env.ref(
                'techfuge_customisation.email_template_exhibitor_registration_mail_to_exhibitor')
        mail_template.sudo().with_user(user.id).send_mail(self.id, force_send=True)


        # user = self.env.ref('base.user_admin')
        # mail_template = self.env.ref(
        #     'techfuge_customisation.email_template_exhibitor_registration_mail_to_exhibitor')
        # mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)
        #



    def copy(self, default=None):
        if default is None:
            default = {}
        if 'is_duplicate' not in default:
            default['is_duplicate'] = True
            default['state_id'] = 1

        return super().copy(default)

    def send_exhibitor_registration_mail_to_planner(self):
        user = self.env.ref('base.user_admin')
        if self.event_id:
            mail_template = self.event_id.exhibitor_registration_duplicate_mail_to_planner
        else:
            mail_template = self.env.ref(
                'techfuge_customisation.email_template_exhibitor_registration_mail_to_planner')
        mail_template.sudo().with_user(user.id).send_mail(self.id, force_send=True)


    def send_exhibitor_registration_duplicate_mail_to_planner(self):
        user = self.env.ref('base.user_admin')
        if self.event_id:
            mail_template =   self.event_id.exhibitor_registration_duplicate_mail_to_planner
        else:
            mail_template = self.env.ref(
                'techfuge_exhibitor_customisation.email_template_exhibitor_registration_duplicate_mail_to_planner')
        mail_template.sudo().with_user(user.id).send_mail(self.id, force_send=True)
    @api.model_create_multi
    def create(self, vals_list):
        res = super(CRMLead, self).create(vals_list)

        partner_full_name = ''
        if res.title_abbr:
            partner_full_name += res.title_abbr + ' '
        if res.contact_name:
            partner_full_name += res.contact_name + ' '
        if res.last_name:
            partner_full_name += res.last_name
        res.partner_full_name = partner_full_name

        if res.event_id and res.event_id.analytic_account_id:
            res.analytic_account_id = res.event_id.analytic_account_id.id

        if res.event_id:
            if res.partner_name:
                res.name = res.event_id.name + ' -  ' + res.partner_name

            if res.is_duplicate:
                res.send_exhibitor_registration_duplicate_mail_to_planner()
                res.send_exhibitor_registration_mail_to_planner()
                res.sent_registration_mails = True
            else:
                if not res.source_of_registration == 'excel_upload':
                    res.send_exhibitor_registration_mail_to_exhibitor()
                    res.send_exhibitor_registration_mail_to_planner()
                    res.sent_registration_mails = True

        return res

    def write(self, vals):
        res = super().write(vals)
        print(vals)
        if vals:
            if 'partner_name' in vals and vals['partner_name']:
                if self.partner_id and self.partner_id.parent_id:
                    self.partner_id.parent_id.name = vals['partner_name']
            if 'brand_id' in vals or 'reference_id' in vals or 'company_name' in vals or 'street' :
                if self.order_ids:
                    for order in self.order_ids:
                        if 'brand_id' in vals and vals['brand_id']:
                            order.brand_id = vals['brand_id']
                        if 'reference_id' in vals and vals['reference_id']:
                            order.reference_id = vals['reference_id']
                        if 'company_name' in vals and vals['company_name']:
                            if order.exhibitor_contract_id:
                                order.exhibitor_contract_id.company_name = vals['company_name']
                        if 'street' in vals and vals['street']:
                            if order.exhibitor_contract_id:
                                order.exhibitor_contract_id.company_address = vals['street']
            if 'agent_id' in vals:
                if self.partner_id:
                    self.partner_id.agent_id = vals['agent_id']
        return res

    @api.onchange('event_id')
    def onchange_event_id(self):
        if self.event_id:
            self.analytic_account_id = self.event_id.analytic_account_id.id,
            self.user_id = self.event_id.sales_person_id.id,
            self.team_id = self.event_id.sales_team_id.id

    @api.onchange('agent_id')
    def onchange_agent_id(self):
        if self.agent_id:
            self.email_from = self.agent_id.email

    def _prepare_contact_name_from_partner(self, partner):
        res = super()._prepare_contact_name_from_partner(partner=partner)
        if self.event_id:
            res['contact_name'] = self.contact_name
        return res

    def action_send_exhibitor_registration_mails(self):
        for lead in self.filtered(lambda l: not l.sent_registration_mails):
            if lead.event_id:
                lead.send_exhibitor_registration_mail_to_exhibitor()
                lead.send_exhibitor_registration_mail_to_planner()
                lead.sent_registration_mails = True

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super()._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)

        if partner_name == self.contact_name:
            res['name'] = self.partner_full_name

        if self.event_id and res['is_company']:
            res['customer_rank'] = 1
            res['email'] = False

        if self.additional_email:
            res['additional_email'] = self.additional_email
            res['agent_id'] = self.agent_id.id if self.agent_id else False

        return res

    def _prepare_opportunity_quotation_context(self):
        res = super()._prepare_opportunity_quotation_context()
        if self.event_id:
            if self.analytic_account_id:
                analytic_account = self.analytic_account_id
            else:
                analytic_account = self.event_id.analytic_account_id
            res['default_analytic_account_id'] = analytic_account.id
            res['default_event_id'] = self.event_id.id
            res['default_brand_id'] = self.brand_id.id
            res['default_reference_id'] = self.reference_id.id
            res['default_so_type'] = 'agreement'
        return res

    @api.depends('order_ids')
    def _compute_sale_order_state(self):
        for lead in self:
            lead.sale_order_state = False
            for order in lead.order_ids:
                if order.so_type == 'agreement':
                    order_state = dict(order._fields['state'].selection).get(order.state)
                    lead.sale_order_state = order_state
