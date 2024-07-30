# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SOStandDetails(models.Model):
    _name = 'so.stand.details'
    _description = 'Sale Order Stand Details'
    _rec_name = 'stand_id'

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    hall_id = fields.Many2one("event.activity.location", string="Hall")
    stand_id = fields.Many2one("exhibitor.stand.details", string="Stand Number")
    stand_number = fields.Char(string="Stand")
    stand_description = fields.Char(string="Description")
    stand_width = fields.Float(string="Width (m)")
    stand_depth = fields.Float(string="Depth (m)")
    stand_size = fields.Float(string="Stand Size")

    @api.onchange('stand_id')
    def onchange_stand_id(self):
        if self.stand_id:
            self.hall_id = self.stand_id.hall_id.id
            self.stand_number = self.stand_id.stand_number
            self.stand_description = self.stand_id.stand_description
            self.stand_width = self.stand_id.stand_width
            self.stand_depth = self.stand_id.stand_depth
            self.stand_size = self.stand_id.stand_size
