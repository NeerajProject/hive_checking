# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorOtherRequest(models.Model):
    _name = 'exhibitor.other.request'
    _description = 'Exhibitor Other Requests'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    contractor_details_id = fields.Many2one("exhibitor.contractor.details", string="Contractor Details")
    event_id = fields.Many2one("event.event", string="Event")
    product_template_id = fields.Many2one("product.template", string="Product")
    name = fields.Char(string="Description", related="product_template_id.display_name")
    # unit_of_measure = fields.Many2one(comodel_name='uom.uom',
    #     string='Unit of Measure', related="product_template_id.uom_id",store=True)
    product_uom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure')
    price_unit = fields.Float(string="Unit Price", digits='Product Price')
    price_list_id = fields.Many2one('product.pricelist', string="Price List")
    tax_ids = fields.Many2many('account.tax', string='Taxes',
                               domain=['|', ('active', '=', False), ('active', '=', True)])
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    currency_id = fields.Many2one(related='price_list_id.currency_id', store=True, string='Currency', readonly=True)

    @api.depends('product_uom_qty', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        print("TEST PORTALLLLLLLLLLLL")
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])

            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })

    def _convert_to_tax_base_line_dict(self):
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.exhibitor_contract_id.sale_order_id.partner_id,
            currency=self.price_list_id.currency_id,
            product=self.product_template_id.product_variant_id,
            taxes=self.tax_ids,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            price_subtotal=self.price_subtotal,
        )
