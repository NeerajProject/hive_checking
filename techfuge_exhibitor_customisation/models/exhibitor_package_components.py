# -*- coding: utf-8 -*-

from odoo import api, fields, _, models


class ExhibitorPackageComponents(models.Model):
    _name = 'exhibitor.package.components'
    _description = 'Exhibitor Package Components'

    product_template_id = fields.Many2one('product.template', string="Package")
    product_id = fields.Many2one('product.product', string="Component")
    name = fields.Char(string="Description")
    quantity = fields.Integer(string="Quantity")
    uom_id = fields.Many2one("uom.uom", string="UoM")
    price = fields.Float(string="Unit Price", compute="_compute_component_price", readonly=False)
    sale_order_id = fields.Many2one('sale.order', string="Order")
    move_id = fields.Many2one("account.move", string="Invoice")
    total_price = fields.Float(string="Total", compute='_compute_components_total')
    company_id = fields.Many2one(related='sale_order_id.company_id')
    currency_id = fields.Many2one(related='sale_order_id.currency_id')
    pricelist_id = fields.Many2one('product.pricelist', related='sale_order_id.pricelist_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id.id

    @api.depends('product_id', 'uom_id', 'quantity')
    def _compute_component_price(self):
        for component in self:
            component.price = 0
            if component.pricelist_id and component.product_id and component.uom_id and component.quantity:
                product = component.product_id
                uom = component.uom_id
                qty = component.quantity
                component.price = component.sale_order_id.pricelist_id._get_product_price(product, qty, uom=uom)

    @api.depends('quantity', 'price')
    def _compute_components_total(self):
        for component in self:
            component.total_price = 0
            if component.quantity and component.price:
                component.total_price = component.quantity * component.price

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.sale_order_id.partner_id,
            currency=self.sale_order_id.currency_id,
            product=self.product_id,
            taxes=self.product_id.taxes_id,
            price_unit=self.price,
            quantity=self.quantity,
            price_subtotal=self.total_price,
        )
