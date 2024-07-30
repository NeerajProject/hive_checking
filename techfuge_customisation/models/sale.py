# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_id = fields.Many2one('event.event', string='Event')

    def _create_invoices(self, grouped=False, final=False, date=None):
        """ Override to add event id """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        if invoices:
            for order in self:
                invoices.write({
                    'sale_id': order.id,
                    'event_id': order.event_id.id if order.event_id else False
                })
        return invoices


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    event_event_id = fields.Many2one('event.event', string='Event ID')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.order_id.event_id:
            res.event_event_id = res.order_id.event_id
        return res
