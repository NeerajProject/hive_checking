# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char(string="Fax")
    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    additional_email = fields.Char(string="Customer Email")
    agent_id = fields.Many2one("res.partner", string="Agent")
    is_agent = fields.Boolean(string="Is Agent")
    code_country = fields.Char(string="Country Code")


    def write(self, vals):

        if 'email' in vals:
            if self.agent_id:
                if vals['email'] != self.agent_id.email:
                    vals['email'] = self.agent_id.email

        res = super(ResPartner, self).write(vals)
        print(res)
        exhibitor_contract_vals = {}
        print("<<<<<<<<<<<<<<>>>>>>>>>>",vals)
        if self.exhibitor_contract_id:
            if 'parent_id' in vals:
                exhibitor_contract_vals['company_name'] = self.env['res.partner'].search([('id','=',int(vals['parent_id']))]).name
            if 'name' in vals:
                exhibitor_contract_vals['exhibitor_name'] = vals['name']
            if 'country_id' in vals:
                country = self.env['res.country'].browse(vals['country_id'])
                exhibitor_contract_vals['country_name'] = country.name
            if 'phone' in vals:
                exhibitor_contract_vals['landline'] = vals['phone']
            if 'mobile' in vals:
                exhibitor_contract_vals['mobile'] = vals['mobile']
            if 'additional_email' in vals:
                exhibitor_contract_vals['email'] = vals['additional_email']
            self.exhibitor_contract_id.update(exhibitor_contract_vals)

        if self.child_ids and self.company_type == 'company':
            if 'name' in vals:
                exhibitor_contract_vals['company_name'] = vals['name']

            company_address = ''
            if self.street:
                company_address += self.street + ', '
            if self.city:
                company_address += self.city + ', '
            if self.state_id:
                company_address += self.state_id.name

            exhibitor_contract_vals['company_address'] = company_address

            for child in self.child_ids:
                if child.exhibitor_contract_id:
                    child.exhibitor_contract_id.update(exhibitor_contract_vals)

        return res
