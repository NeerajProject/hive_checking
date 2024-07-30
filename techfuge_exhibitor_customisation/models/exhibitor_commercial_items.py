# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorCommercialItems(models.Model):
    _name = 'exhibitor.commercial.items'
    _description = 'Exhibitor Commercial Items'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    product_template_id = fields.Many2one("product.template", string="Product")
    name = fields.Char(string="Description")
    product_uom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    product_uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Unit Price", digits='Product Price')
    tax_ids = fields.Many2many("account.tax", string="Taxes")
    company_id = fields.Many2one(related='exhibitor_contract_id.company_id', store=True)
    currency_id = fields.Many2one(related='exhibitor_contract_id.currency_id', store=True)
    price_subtotal = fields.Monetary(string="Subtotal")
    price_tax = fields.Float(string="Total Tax")
    price_total = fields.Monetary(string="Total")
