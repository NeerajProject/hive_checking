# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta


class Event(models.Model):
    _inherit = 'event.event'

    build_up_date = fields.Datetime(string='Build Up Date')
    event_ref_no = fields.Char(string='Event Reference No.', default=lambda self: _('New'), readonly=True, copy=False)
    attendee_reg_no_prefix = fields.Char("Attendee Reg. No. Prefix")
    sales_person_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user,
                                      tracking=True)
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', check_company=True, tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    activity_location_ids = fields.One2many("event.activity.location", "event_id", string="Activity Location")


    buyer_image_template = fields.Image(string="Buyer Image Template",attachment=True)
    contractor_image_template = fields.Image(string="Contractor Image Template")
    vip_image_template = fields.Image(string="VIP Buyer Image Template")
    vip_hosted_template = fields.Image(string="VIP Hosted  Image Template")
    exhibitor_template = fields.Image(string="Exhibitor VIP Image Template")

    special_include = fields.Html(string="Special Inclusion")
    special_include_part_b = fields.Html(string="Special Inclusion Part B")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('event_ref_no', _("New")) == _("New"):
                vals['event_ref_no'] = self.env['ir.sequence'].next_by_code('event.reference.number') or _("New")
        return super().create(vals_list)

    @api.model
    def _cron_create_event_for_next_year(self):
        """ Creates the same event for next year. """
        events = self.sudo().search([])
        current_date = fields.Datetime.now() + timedelta(days=365)
        for event in events:
            next_yr_date_begin = event.date_begin + timedelta(days=365)
            next_yr_date_end = event.date_end + timedelta(days=365)
            existing_event = self.sudo().search([('name', '=', event.name), ('date_begin', '=', next_yr_date_begin),
                                                 ('date_end', '=', next_yr_date_end)])
            if current_date.year == next_yr_date_begin.year:
                if not existing_event:
                    new_event = event.copy()
                    new_event.sudo().write({
                        'name': event.name,
                        'date_begin': next_yr_date_begin,
                        'date_end': next_yr_date_end
                    })
