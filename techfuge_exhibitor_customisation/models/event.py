# -*- coding: utf-8 -*-

from odoo import api, fields, models, _



class EventBankAccounts(models.Model):
    _name = 'report.bank.details'
    name = fields.Char()
    account_number = fields.Char(string="Account Number")
    iban_number = fields.Char(string="IBAN NUMBER")
    swift_code = fields.Char(string="Swift Code")
    bank_address = fields.Char(string="Bank Address")
    bank_name = fields.Char(string="Bank Name")
    branch_name = fields.Char(string="Branch Name")
    country_id = fields.Many2one('res.country',string="Country")

class Event(models.Model):
    _inherit = 'event.event'

    exhibitor_contracts_count = fields.Integer(string='No. of Contracts', store=False, readonly=True,
                                               compute='_compute_exhibitor_contracts_count')
    exhibitor_stand_ids = fields.One2many("exhibitor.stand.details", "event_id", string="Stand Details")
    event_logo = fields.Binary(string="Event Logo")
    checkin_date = fields.Date(string="Check In Date")
    checkout_date = fields.Date(string="Check Out Date")
    allowed_no_of_nights = fields.Integer(string="Allowed No. of Nights")
    rate_per_additional_night = fields.Float(string="Rate per Additional Night ($)")
    contractor_details_count = fields.Integer(string='Contractor Count', store=False, readonly=True,
                                              compute='_compute_contractor_details_count')
    last_booking_hotel = fields.Date(string="Last Booking Day")

    event_key = fields.Char(string="Key",compute="_compute_event_key")
    visitors_urls = fields.Char(compute="compute_url_for_visitors")
    is_onsite = fields.Boolean(string="Is Onsite")
    is_different_bank_account = fields.Boolean(string="Different Bank Accounts")
    bank_details_ids = fields.Many2many('report.bank.details',string="Bank Details")

    # custom crm template

    exhibitor_registeration_template =  fields.Many2one('mail.template',string="Exhibitor Registration")
    exhibitor_registration_duplicate_mail_to_planner =  fields.Many2one('mail.template',string="Exhibitor Duplicate  Registration")


    def get_bank_details(self,partner_id):
        is_country_exist = self.bank_details_ids.filtered(lambda l:l.country_id == partner_id.country_id)
        if is_country_exist:
            for rec in is_country_exist:
                return rec
        else:
            for rec in  self.bank_details_ids:
                if rec.country_id:
                    pass
                else:
                    return rec

    def compute_url_for_visitors(self):
        for rec in self:
            if rec.event_key:
                rec.visitors_urls = str(rec.get_base_url())+"/create/visit/badge/onsite?token="+(rec.event_key)
            else:
                rec.visitors_urls = ''

    def _compute_event_key(self):
        for rec in self:
            rec.event_key = hash(str(rec.id)+str(rec.name))


    emails = fields.Char()
    place_of_supply = fields.Char()
    event_details = fields.Html()
    header_logo_description = fields.Html()
    exhibitor_template_name = fields.Char()
    is_portal_attendee_enable = fields.Boolean(string="Enable Portal Attendee Creation")

    # added event

    branding_panel_width = fields.Float()
    branding_panel_height = fields.Float()
    embassy_details = fields.Char(string="Embassy")
    exhibitor_stand_count = fields.Integer(compute="_compute_exhibitor_stand_count")


    def _compute_exhibitor_stand_count(self):
        for rec in self:
            rec.exhibitor_stand_count = len(rec.exhibitor_stand_ids)




    def view_event_stand_details(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'exhibitor.stand.details',
            'name': _('Stand Details '+str(self.name)),
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('event_id', '=', self.id)],
        }




    def _compute_exhibitor_contracts_count(self):
        for event in self:
            exhibitor_contracts_count = self.env['exhibitor.contract'].sudo().search_count(
                [('event_id', '=', event.id)])
            event.exhibitor_contracts_count = exhibitor_contracts_count

    def action_view_contractor_details(self):
        self.ensure_one()

        action = {
            'name': _("Contractor Details"),
            'type': 'ir.actions.act_window',
            'res_model': 'exhibitor.contractor.details',
            'target': 'current',
        }

        contractors = self.env['exhibitor.contractor.details'].search([('event_id', '=', self.id)])
        contractor_details_ids = contractors.ids

        if len(contractor_details_ids) == 1:
            contractor = contractor_details_ids[0]
            action['res_id'] = contractor
            action['view_mode'] = 'form'
            action['views'] = [(
                self.env.ref('techfuge_exhibitor_customisation.view_exhibitor_contractor_details_form').id, 'form'
            )]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', contractor_details_ids)]
        return action

    def _compute_contractor_details_count(self):
        for event in self:
            contractors = self.env['exhibitor.contractor.details'].search([('event_id', '=', event.id)])
            event.contractor_details_count = len(contractors)
