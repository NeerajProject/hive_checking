# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorPaymentStages(models.Model):
    _name = 'exhibitor.payment.stages'
    _description = 'Exhibitor Payment Stages'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    move_id = fields.Many2one("account.move", string="Invoice")
    name = fields.Char(string="Description")
    payment_type = fields.Selection(selection=[
        ('percentage', 'Percentage'),
        ('amount', 'Amount')
    ], string="Type")
    paid_percentage = fields.Float(string="Percentage(%)")
    paid_amount = fields.Float(string="Amount", compute="_compute_paid_amount")
    payment_due_date = fields.Date(string="Due Date")
    currency_id = fields.Many2one(related='sale_order_id.currency_id')
    exhibitor_contract_currency_id = fields.Many2one(
        related='exhibitor_contract_id.currency_id', string="Contract Currency")



    @api.onchange('paid_percentage')
    def onchange_paid_description(self):
        if self.sale_order_id.is_new_payment_template():
            name = self.name.split("@")
            self.name = name[0]+"@"+self.sale_order_id.currency_id.name+" "+str(self.paid_amount)+" / "+self.sale_order_id.currency_id.name+" "+str(self.sale_order_id.amount_total)+"   : ON OF BEFORE "


    @api.depends('paid_percentage', 'sale_order_id.order_line')
    def _compute_paid_amount(self):
        for payment in self:
            payment.paid_amount = 0
            if payment.paid_percentage:
                if payment.sale_order_id:
                    amount_total = payment.sale_order_id.amount_total
                else:
                    amount_total = payment.exhibitor_contract_id.so_amount_total
                paid_amount = (amount_total * payment.paid_percentage) / 100
                payment.paid_amount = paid_amount
