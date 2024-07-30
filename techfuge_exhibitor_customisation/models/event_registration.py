# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
class ResCountryCodeMaster(models.Model):
    _name = 'res.country.code.master'
    _rec_name = 'code'
    code =  fields.Char(string='Code')
    country = fields.Char(string="Country")


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_full_name = fields.Char(string="Exhibitor Name", related='exhibitor_contract_id.exhibitor_name')
    contractor_details_id = fields.Many2one("exhibitor.contractor.details", string="Contractor Contract")
    contractor_name = fields.Char(string="Contractor Name", related='contractor_details_id.contractor_full_name')
    passport_attachment_id = fields.Many2one('ir.attachment', string="Passport Copy Attachment")
    visa_attachment_id = fields.Many2one('ir.attachment', string="Visa Copy Attachment")
    air_ticket_attachment_id = fields.Many2one('ir.attachment', string="Air Ticket Attachment")
    country_code  = fields.Many2one('res.country.code.master',string='Code')
    def get_mobile_with_country_code(self):
        code = ''
        if self.country_code:
            code = self.country_code.code +" - "
        if self.mobile:
            code = code+self.mobile
        return code

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'event_id' not in vals:
                if 'exhibitor_contract_id' in vals and vals['exhibitor_contract_id']:
                    exhibitor_contract_id = self.env['exhibitor.contract'].sudo().browse(vals['exhibitor_contract_id'])
                    if exhibitor_contract_id:
                        vals['event_id'] = exhibitor_contract_id.event_id.id
                if 'attendee_full_name' in vals and vals['attendee_full_name']:
                    attendee_full_name = vals['attendee_full_name'].split(' ')
                    if len(attendee_full_name) > 1:
                        first_name = attendee_full_name[0]
                        last_name = attendee_full_name[1]
                    else:
                        first_name = attendee_full_name[0]
                        last_name = ''
                    vals['name'] = first_name
                    vals['last_name'] = last_name
        return super(EventRegistration, self).create(vals_list)

    def download_exhibitor_attendee_attachments(self):
        self.ensure_one()

        context = self.env.context
        if context.get('passport_copy'):
            attachment_id = self.passport_attachment_id.id
        elif context.get('visa_copy'):
            attachment_id = self.visa_attachment_id.id
        elif context.get('air_ticket'):
            attachment_id = self.air_ticket_attachment_id.id
        else:
            attachment_id = self.badge_attachment_id.id

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment_id,
            'target': 'self',
        }
