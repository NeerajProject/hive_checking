# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class Opportunity2Quotation(models.TransientModel):
    _inherit = 'crm.quotation.partner'

    def action_apply(self):
        parent_id = False
        lead = self.lead_id
        if self.action == 'create':
            parent_id = self.env['res.partner'].sudo().search([('name', '=', lead.partner_name)], limit=1)
        elif self.action == 'exist':
            parent_id = self.partner_id
        if lead.event_id and parent_id:
            email_parts = tools.email_split(lead.email_from)
            partner_vals = {
                'name': lead.partner_name,
                'user_id': self.env.context.get('default_user_id') or lead.user_id.id,
                'comment': lead.description,
                'team_id': lead.team_id.id,
                'parent_id': parent_id.id,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': email_parts[0] if email_parts else False,
                'title': lead.title.id,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id.id,
                'state_id': lead.state_id.id,
                'website': lead.website,
                'is_company': False,
                'type': 'contact'
            }
            if lead.lang_id:
                partner_vals['lang'] = lead.lang_id.code
            partner = self.env['res.partner'].sudo().create(partner_vals)
            lead.partner_id = partner.id
        else:
            return super().action_apply()
