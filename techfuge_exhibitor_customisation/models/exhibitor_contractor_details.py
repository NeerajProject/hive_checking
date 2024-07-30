# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import random

import base64

class ExhibitorContractorDetails(models.Model):
    _name = 'exhibitor.contractor.details'
    _description = 'Exhibitor Contractor Details'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', default=lambda self: _('New'), readonly=True)
    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_name = fields.Char(string="Exhibitor Name", related="exhibitor_contract_id.exhibitor_name")
    event_id = fields.Many2one("event.event", string="Event", readonly=True)
    title = fields.Selection(selection=[
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ], string='Title', default='Mr.')
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    contractor_full_name = fields.Char(string="Contractor Name", compute='_compute_contractor_full_name')
    company_name = fields.Char(string="Company")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    landline = fields.Char(string="Landline")
    designation = fields.Char(string="Designation")
    company_address = fields.Char(string="Company Address")
    city_or_town = fields.Char(string="City / Town")
    state_or_province = fields.Char(string="State / Province")
    country_id = fields.Many2one("res.country", string="Country")
    upload_permit = fields.Binary(string="Upload Permit")
    permit_attachment_id = fields.Many2one("ir.attachment", string="Permit Attachment")
    status = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('access_granted', 'Portal Access Granted'),
    ], default="pending", string="Status")
    no_of_badges = fields.Integer(string="Badge Count")
    contractor_user_id = fields.Many2one('res.users', string='Contractor User')
    contractor_user_login = fields.Char(string='Contractor User Login')
    contractor_user_password = fields.Char(string='Contractor User Password')
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    other_request_ids = fields.One2many("exhibitor.other.request", "contractor_details_id",
                                        string="Other Requests")
    badge_ids = fields.One2many("event.registration", "contractor_details_id", string="Badge Details")
    uploaded_document_ids = fields.One2many("exhibitor.uploaded.documents", "contractor_details_id",
                                            string="Uploaded Documents")
    contractor_other_request_count = fields.Integer(string='Other Request Count', store=False, readonly=True,
                                                    compute='_compute_contractor_other_request_count')
    contractor_invoice_count = fields.Integer(string='Invoice Count', store=False, readonly=True,
                                              compute='_compute_contractor_invoice_count')
    contractor_payments_count = fields.Integer(string='Payments Count', store=False, readonly=True,
                                               compute='_compute_contractor_payments_count')
    brand_id = fields.Many2one('res.brand', string='Brand')
    enable_finance_section = fields.Boolean(string="Enable Finance Section", default=True)
    contract_purpose_id = fields.Many2one('contract.purpose', string='Contract Purpose')
    exhibitor_user_id = fields.Many2one('res.users',copy=False)
    attendee_id = fields.Many2one('event.registration')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code('contractor.contract') or _("New")
        return super(ExhibitorContractorDetails, self).create(vals_list)

    @api.depends('title', 'first_name', 'last_name')
    def _compute_contractor_full_name(self):
        for contractor in self:
            contractor_full_name = ''
            if contractor.title:
                contractor_full_name += contractor.title + ' '
            if contractor.first_name:
                contractor_full_name += contractor.first_name + ' '
            if contractor.last_name:
                contractor_full_name += contractor.last_name
            contractor.contractor_full_name = contractor_full_name

    def write(self, vals):
        if 'upload_permit' in vals:
            permit_attachment = self.env['ir.attachment'].sudo().create({
                'name': 'Contractor Permit',
                'datas': vals['upload_permit'],
                'type': 'binary',
                'public': True
            })
            vals['permit_attachment_id'] = permit_attachment.id
        return super().write(vals)

    def action_view_contractor_other_requests(self):
        self.ensure_one()

        action = {
            'name': _("Sale Orders"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }

        other_requests = self.env['sale.order'].search(
            [('partner_id', '=', self.partner_id.id), ('event_id', '=', self.event_id.id),
             ('is_other_request', '=', True)])
        other_request_ids = other_requests.ids

        if len(other_request_ids) == 1:
            other_request = other_request_ids[0]
            action['res_id'] = other_request
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', other_request_ids)]
        return action

    def _compute_contractor_other_request_count(self):
        for contractor in self:
            other_requests = self.env['sale.order'].search(
                [('partner_id', '=', contractor.partner_id.id), ('event_id', '=', contractor.event_id.id),
                 ('is_other_request', '=', True)])
            contractor.contractor_other_request_count = len(other_requests)

    def action_view_contractor_invoices(self):
        self.ensure_one()

        action = {
            'name': _("Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'target': 'current',
        }

        invoices = self.env['account.move'].search(
            [('partner_id', '=', self.partner_id.id), ('event_id', '=', self.event_id.id)])
        invoice_ids = invoices.ids

        if len(invoice_ids) == 1:
            invoice = invoice_ids[0]
            action['res_id'] = invoice
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', invoice_ids)]
        return action

    def _compute_contractor_invoice_count(self):
        for contractor in self:
            invoices = self.env['account.move'].search(
                [('partner_id', '=', contractor.partner_id.id), ('event_id', '=', contractor.event_id.id)])
            contractor.contractor_invoice_count = len(invoices)

    def action_view_contractor_payments(self):
        self.ensure_one()

        action = {
            'name': _("Payments"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'target': 'current',
        }

        payments = self.env['account.payment'].search(
            ['|', ('partner_id', '=', self.partner_id.parent_id.id), ('partner_id', '=', self.partner_id.id)])
        payment_ids = payments.ids

        if len(payment_ids) == 1:
            payment = payment_ids[0]
            action['res_id'] = payment
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', payment_ids)]
        return action

    def _compute_contractor_payments_count(self):
        for contractor in self:
            payments = self.env['account.payment'].search(
                ['|', ('partner_id', '=', contractor.partner_id.parent_id.id),
                 ('partner_id', '=', contractor.partner_id.id)])
            contractor.contractor_payments_count = len(payments)

    def approve_contractor(self):
        partner_obj = self.env['res.partner'].sudo()
        state = False

        if  True:
            if self.contractor_full_name and self.email:
                if self.state_or_province:
                    state = self.env['res.country.state'].search([('name', '=', self.state_or_province)])



                contractor_partner = partner_obj.create({
                    'name': self.contractor_full_name,
                    'mobile': self.mobile,
                    'email': self.email,
                    'company_name': self.company_name,
                    'phone': self.landline,
                    'function': self.designation,
                    'street': self.company_address,
                    'city': self.city_or_town,
                    'state_id': state.id if state else False,
                    'country_id': self.country_id.id if self.country_id else False,
                })
                ticket=self.env['event.registration'].create({
                    'name': self.first_name,
                    'last_name': self.last_name,
                    'company_name':self.company_name,
                    'email':self.email,
                    'event_id':self.event_id.id,
                    'country_id':self.country_id.id,
                    'exhibitor_contract_id':self.exhibitor_contract_id.id,
                    'attendee_type_id': self.env.ref('techfuge_customisation.attendee_type_data_contractor').id,
                    'not_contractor_sent_from_portal':False

                })
                self.attendee_id = ticket

                ticket.exhibitor_contract_id = self.exhibitor_contract_id
                if not contractor_partner.parent_id:
                    contractor_partner.create_company()

                self.sudo().write({
                    'partner_id': contractor_partner.id,
                })

                self.status = 'approved'

    def generate_random_password(self):
        """ Returns random password string containing alphanumeric characters """

        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pw_length = 8
        password = ""
        for i in range(pw_length):
            next_index = random.randrange(len(alphabet))
            password = password + alphabet[next_index]
        return password

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

                user = self.env.ref('base.user_admin')
                mail_template = self.env.ref(
                    'techfuge_exhibitor_customisation.email_template_contractor_dashboard_approved_mail'
                )
                # CUSTOM CODE
                if self.attendee_id:
                    # report_template_id = self.attendee_id.attendee_type_id.report_template_id._render_qweb_pdf(self.attendee_id.id)
                    print("yes")
                    report_template_id = self.env['ir.actions.report']._render_qweb_pdf("techfuge_exhibitor_customisation.action_report_contractor_badge", self.attendee_id.id)
                    data_record = base64.b64encode(report_template_id[0])
                    ir_values = {
                        'name': self.attendee_id.attendee_full_name+".pdf",
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/x-pdf',
                    }
                    data_id = self.env['ir.attachment'].create(ir_values)
                    mail_template.attachment_ids = [(6, 0, [data_id.id])]






                mail_template.with_user(user.id).sudo().with_context(
                    contractor_full_name=self.contractor_full_name).send_mail(
                    self.id, force_send=True
                )

                self.status = 'access_granted'
        else:
            if self.contractor_full_name and self.email:
                contractor_user = res_users.search([('login','=',self.email)])
                # print(contractor_user)
                # self.contractor_user_id = contractor_user
                self.sudo().write({
                    'contractor_user_id': contractor_user.id,
                    'contractor_user_login': contractor_user.login,
                    'exhibitor_user_id': contractor_user.id
                })
                contractor_user.event_id = self.event_id
                user = self.env.ref('base.user_admin')
                mail_template = self.env.ref(
                    'techfuge_exhibitor_customisation.email_template_contractor_dashboard_approved_mail'
                )
                # CUSTOM CODE
                if self.attendee_id:
                    # report_template_id = self.attendee_id.attendee_type_id.report_template_id._render_qweb_pdf(self.attendee_id.id)
                    print("yes")
                    report_template_id = self.env['ir.actions.report']._render_qweb_pdf(
                        "techfuge_exhibitor_customisation.action_report_contractor_badge", self.attendee_id.id)
                    data_record = base64.b64encode(report_template_id[0])
                    ir_values = {
                        'name': self.attendee_id.attendee_full_name + ".pdf",
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/x-pdf',
                    }
                    data_id = self.env['ir.attachment'].create(ir_values)
                    mail_template.attachment_ids = [(6, 0, [data_id.id])]

                mail_template.with_user(user.id).sudo().with_context(
                    contractor_full_name=self.contractor_full_name).send_mail(
                    self.id, force_send=True
                )

                self.status = 'access_granted'