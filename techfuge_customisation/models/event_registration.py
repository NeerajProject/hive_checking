# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta
import qrcode
import base64
from io import BytesIO
from werkzeug import urls
from odoo.exceptions import ValidationError
import base64


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    not_contractor_sent_from_portal = fields.Boolean(default=True)
    attendee_id = fields.Integer(string="Attendee ID", compute="_compute_attendee_id")
    attendee_reg_no = fields.Char(string='Registration No.', default=lambda self: _('New'), readonly=True)
    title = fields.Selection(selection=[
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ], string='Title', default='Mr.')
    last_name = fields.Char(string="Last Name")
    attendee_full_name = fields.Char(string="Attendee Full Name", compute='_compute_attendee_full_name', store=False)
    designation = fields.Char(string="Designation")
    company_name = fields.Char(string="Company Name")
    company_website = fields.Char(string="Company Website")
    company_address = fields.Char(string="Company Address")
    city_or_town = fields.Char(string="City / Town")
    state_or_province = fields.Char(string="State / Province")
    country_id = fields.Many2one('res.country', string="Country")
    attendee_type_id = fields.Many2one("event.attendee.type", string="Attendee Type", tracking=True)
    attendee_parent_type = fields.Selection(string='Type', related='attendee_type_id.type')
    badge_mail_template_id = fields.Many2one('mail.template', string='Mail Template',
                                             related='attendee_type_id.badge_mail_template_id')

    nature_of_business_id = fields.Many2one("event.business.nature", string='Nature of Business')
    purpose_of_visit_ids = fields.Many2many("event.visit.purpose", string='Purpose of Visit')
    source_of_knowledge_id = fields.Many2one("event.knowledge.source", string='How did you come to know about HIVE?')
    role_description = fields.Selection(selection=[
        ('Final Decision Maker', 'Final Decision Maker'),
        ('Key Influencer', 'Key Influencer'),
        ('Advisor', 'Advisor'),
    ], string='What best describe your role?')
    no_of_stores = fields.Selection(selection=[
        ('less than 5', 'less than 5'),
        ('5-10', '5-10'),
        ('10 or more', '10 or more'),
        ('Non Applicable', 'Non Applicable'),
    ], string='How many number of stores you have?')
    annual_revenue_enterprise = fields.Selection(selection=[
        ('Annual turnover up to $10 ML', 'Annual turnover up to $10 ML'),
        ('Annual turnover $10-50 ML', 'Annual turnover $10-50 ML'),
        ('Annual turnover over $50 ML', 'Annual turnover over $50 ML'),
    ], string='Annual Revenue of the enterprise')
    interested_product_categories_ids = fields.Many2many("interested.product.categories",
                                                         string='Product Categories Interested')
    first_visit_exhibition = fields.Selection(selection=[
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string='Is this your first time to visit the exhibition?')

    exhibitor_company_name = fields.Char(string="Exhibitor Company Name")
    exhibitor_company_website = fields.Char(string="Exhibitor Company Website")
    exhibitor_company_address = fields.Char(string="Exhibitor Company Address")

    exhibitor_name = fields.Char(string="Exhibitor")
    contractor_company_name = fields.Char(string="Contractor Company Name")
    contractor_company_website = fields.Char(string="Contractor Company Website")
    contractor_company_address = fields.Char(string="Contractor Company Address")

    source_of_registration = fields.Selection(selection=[
        ('from_website', 'Website Registration'),
        ('onsite_registration', 'Onsite Registration'),
        ('excel_upload', 'Excel Upload'),
    ], string='Source of Registration', default='onsite_registration')

    attendee_activities_ids = fields.One2many("event.attendee.activities", "attendee_id", string="Attendee Activities")
    event_reference = fields.Char(string='Event Reference No.', related='event_id.event_ref_no')
    badge_sent = fields.Boolean(string="Badge Sent", default=False)
    badge_attachment_id = fields.Many2one('ir.attachment', string="Badge Attachment")

    checkin_date = fields.Date(string="Check In Date")
    checkout_date = fields.Date(string="Check Out Date")
    no_of_nights = fields.Integer(string="No. of Nights", compute="_compute_number_of_nights")
    eligible_for_flight_ticket = fields.Selection(selection=[
        ('yes', 'Yes'), ('no', 'No')
    ], string="Eligible for Flight Ticket")
    air_fare_claim_value = fields.Selection(selection=[
        ('usd', 'USD'), ('AED', 'AED'), ('euro', 'EURO')
    ], string="Air Fare Claim Value")
    air_fare_claim_date = fields.Date(string="Air Fare Claim Date")
    receiver_signed_cash_receipt = fields.Binary(string="Receiver Signed Cash Receipt")
    passport_copy = fields.Binary(string="Passport Copy")
    visa_copy = fields.Binary(string="Visa")
    air_ticket = fields.Binary(string="Air Ticket")
    is_exhibitor = fields.Boolean(compute ="_compute_is_exhibitor")
    is_vip_buyer = fields.Boolean(compute ="_compute_is_vip_buyer")
    is_buyer = fields.Boolean(compute ="_compute_is_buyer")
    is_contractor = fields.Boolean(compute ="_compute_is_buyer")
    badge_download_url = fields.Char(compute="_compute_badge_download")

    def _compute_badge_download(self):
        for rec in self:
            url = rec.get_base_url()+"/badge/download?id="+str(self.id)
            rec.badge_download_url = url

    def _compute_is_exhibitor(self):
       print(">>>>")
       self.is_exhibitor = self.attendee_type_id.id == self.env.ref('techfuge_customisation.attendee_type_data_exhibitor')

    def _compute_is_vip_buyer(self):
        self.is_vip_buyer = self.attendee_type_id.id == self.env.ref('techfuge_customisation.attendee_type_data_hosted_vip_buyer')

    def _compute_is_buyer(self):
        self.is_buyer = self.attendee_type_id.id == self.env.ref('techfuge_customisation.attendee_type_data_buyer')
    def _compute_is_buyer(self):
      self.is_contractor = self. self.attendee_type_id.id == self.env.ref('techfuge_customisation.attendee_type_data_contractor')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('attendee_reg_no', _("New")) == _("New"):
                if 'event_id' in vals and vals['event_id']:
                    event = self.env['event.event'].sudo().browse(int(vals['event_id']))
                    if event:
                        prefix = event.attendee_reg_no_prefix
                        vals['attendee_reg_no'] = prefix + '/' + self.env['ir.sequence'].next_by_code(
                            'attendee.registration.number') or _("New")

            if 'no_of_stores' in vals and 'annual_revenue_enterprise' in vals:
                if vals['no_of_stores'] == '5-10' or vals['no_of_stores'] == '10 or more':
                    attendee_type_id = self.env.ref('techfuge_customisation.attendee_type_data_vip_buyer')
                elif vals['annual_revenue_enterprise'] == 'Annual turnover $10-50 ML' or \
                        vals['annual_revenue_enterprise'] == 'Annual turnover over $50 ML':
                    attendee_type_id = self.env.ref('techfuge_customisation.attendee_type_data_vip_buyer')
                else:
                    attendee_type_id = self.env.ref('techfuge_customisation.attendee_type_data_buyer')

                if attendee_type_id:
                    if 'attendee_type_id' in vals:
                        if attendee_type_id.id != int(vals['attendee_type_id']):
                            if 'from_visitor_website_form' not in self.env.context:
                                show_warning = False
                            elif 'source_of_registration' in vals and \
                                    vals['source_of_registration'] == 'onsite_registration':
                                show_warning = False
                            else:
                                show_warning = True

                            if show_warning:
                                raise ValidationError(
                                    _('The selected attendee type is not matching the no. of stores and annul revenue '
                                      'of the enterprise. Please change the attendee type.'))
                    else:
                        vals['attendee_type_id'] = attendee_type_id.id

        res = super().create(vals_list)
        for registration in res:
            if registration.source_of_registration == 'onsite_registration':
                if res.not_contractor_sent_from_portal:
                    registration.action_send_visitor_badge_mail()
        return res

    @api.depends('title', 'name', 'last_name')
    def _compute_attendee_full_name(self):
        for attendee in self:
            attendee_full_name = ''
            if attendee.title:
                attendee_full_name += attendee.title + ' '
            if attendee.name:
                attendee_full_name += attendee.name + ' '
            if attendee.last_name:
                attendee_full_name += attendee.last_name
            attendee.attendee_full_name = attendee_full_name

    def _compute_attendee_id(self):
        for attendee in self:
            attendee.attendee_id = attendee.id

    def generate_visitor_badge_qr_code(self):
        url = "/event_registration_details?attendee_id=%s" % str(self.id)
        attendee_record_url = urls.url_join(self.env['ir.config_parameter'].sudo().get_param("web.base.url"), url)
        return attendee_record_url

    def send_visitor_registration_mail(self):
        user = self.env.ref('base.user_admin')
        if self.badge_mail_template_id:
            self.badge_mail_template_id.with_user(user.id).sudo().send_mail(self.id, force_send=True)
            self.get_badge_attachment()

    def action_send_visitor_badge_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'techfuge_customisation.email_template_already_registered_mail_to_visitor')
        if self.attendee_type_id:
            mail_template = self.attendee_type_id.badge_mail_template_id

        for attendee in self.filtered(
                lambda att: att.source_of_registration in ('onsite_registration', 'excel_upload')):
            if not attendee.badge_sent:
                mail_template.with_user(user.id).sudo().send_mail(attendee.id, force_send=True)
                attendee.badge_sent = True
                attendee.get_badge_attachment()

    def get_badge_attachment(self):
        if self.attendee_parent_type == 'exhibitor':
            pdf = self.env['ir.actions.report']._render_qweb_pdf(
                "techfuge_exhibitor_customisation.action_report_exhibitor_badge", self.id
            )[0]
        elif self.attendee_parent_type == 'contractor':
            pdf = self.env['ir.actions.report']._render_qweb_pdf(
                "techfuge_exhibitor_customisation.action_report_contractor_badge", self.id
            )[0]
        else:
            pdf = self.env['ir.actions.report']._render_qweb_pdf(
                "techfuge_customisation.action_report_visitor_badge", self.id
            )[0]

        pdf_data = base64.b64encode(pdf)
        attachment = self.env['ir.attachment'].create({
            'name': self.attendee_full_name + ' - Badge.pdf',
            'type': 'binary',
            'datas': pdf_data,
            'public': True
        })
        self.badge_attachment_id = attachment.id

    @api.depends('checkin_date', 'checkout_date')
    def _compute_number_of_nights(self):
        for rec in self:
            no_of_nights = 0
            if rec.checkin_date and rec.checkout_date:
                date_diff = rec.checkout_date - rec.checkin_date
                no_of_nights = date_diff.days
            rec.no_of_nights = no_of_nights
