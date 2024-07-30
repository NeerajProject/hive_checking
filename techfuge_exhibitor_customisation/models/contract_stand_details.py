# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ContractStandDetails(models.Model):
    _name = 'contract.stand.details'
    _description = 'Contract Order Stand Details'
    _rec_name = 'stand_id'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    hall_id = fields.Many2one("event.activity.location", string="Hall")
    stand_id = fields.Many2one("exhibitor.stand.details", string="Stand Number")
    stand_description = fields.Char(string="Description")
    stand_width = fields.Float(string="Width (m)")
    stand_depth = fields.Float(string="Depth (m)")
    stand_size = fields.Float(string="Stand Size")
