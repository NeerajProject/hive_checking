# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    event_id = fields.Many2one('event.event', string='Event')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    event_id = fields.Many2one('event.event', string='Event')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.move_id.event_id:
            res.event_id = res.move_id.event_id
        return res
