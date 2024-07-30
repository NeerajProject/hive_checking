# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractPurpose(models.Model):
    _name = 'contract.purpose'
    _description = 'Contract Purpose'

    name = fields.Char(string='Name')
