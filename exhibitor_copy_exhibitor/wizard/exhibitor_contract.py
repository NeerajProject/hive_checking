
from odoo import api, fields, models
import random






class ExhibitorContractCopy(models.TransientModel):
    _name = 'exhibitor.contract.copy'
    event_id = fields.Many2one('event.event',string="Event")
    contract_id = fields.Many2one('exhibitor.contract',string="Exhibitor Contract")

    def action_create_duplicate(self):
        opportunity_id=self.contract_id.sale_order_id.opportunity_id.copy()
        opportunity_id.event_id = self.event_id
        if opportunity_id.partner_id:
            pass
        else:
            opportunity_id.partner_id = self.contract_id.partner_id
        opportunity_id.name = self.event_id.name +"-"+ str(opportunity_id.partner_name)
        # sale_order_id = self.env['sale.order'].create({
        #     "partner_id":self.contract_id.partner_id.id,
        #     "brand_id":self.contract_id.brand_id.id,
        #     "event_id":self.event_id.id,
        #     'agreement_sent': False
        # })
        # sale_order_id.opportunity_id = opportunity_id
        # sql ="UPDATE sale_order SET so_type='agreement' WHERE id="+str(sale_order_id.id)
        # self.env.cr.execute(sql)
        #
        #
        # duplicate_contractor_id =self.env['exhibitor.contract'].create({
        #     'exhibitor_name':self.contract_id.exhibitor_name,
        #     'partner_id':self.contract_id.partner_id.id,
        #     'mobile':self.contract_id.mobile,
        #     'email':self.contract_id.email,
        #     'landline':self.contract_id.landline,
        #     'company_name':self.contract_id.company_name,
        #     'company_address':self.contract_id.company_address,
        #     'country_name':self.contract_id.country_name,
        #     'event_id':self.event_id.id,
        #     'dashboard_access':'pending',
        #     'sale_order_id':  sale_order_id.id,
        #
        # })
        #
        # sale_order_id.exhibitor_contract_id = duplicate_contractor_id
        #
        action = {
            'name': "LEAD",
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': "form",
            'target': 'current',
            'res_id': opportunity_id.id

        }
        return  action
class ExhibitorContract(models.Model):
    _inherit = 'exhibitor.contract'
    active = fields.Boolean(default=True)

    def action_duplicate_exhibitor_contract(self):
        action = {
            'name': "Contractor Details",
            'type': 'ir.actions.act_window',
            'res_model': 'exhibitor.contract.copy',
            'target': 'new',
            'view_mode': 'form',

            'context': {

                'default_contract_id': self.id
            }

        }

        return action