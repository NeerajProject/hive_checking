# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorStandDetails(models.Model):
    _name = 'exhibitor.stand.details'
    _description = 'Exhibitor Stand Details'
    _rec_name = 'stand_number'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    event_id = fields.Many2one("event.event", string="Event")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    hall_id = fields.Many2one("event.activity.location", string="Hall")
    stand_number = fields.Char(string="Stand Number")
    stand_description = fields.Char(string="Description")
    stand_width = fields.Float(string="Width (m)")
    stand_depth = fields.Float(string="Depth (m)")
    stand_size = fields.Float(string="Stand Size", compute="_compute_stand_size",digits='Stand Details Unit')

    _sql_constraints = [
        ('name_stand_number', 'unique(hall_id, stand_number , event_id)', 'The stand number must be unique by hall !')
    ]

    @api.depends('stand_width', 'stand_depth')
    def _compute_stand_size(self):
        for stand in self:
            stand.stand_size = 0
            if stand.stand_width and stand.stand_depth:
                stand.stand_size = stand.stand_width * stand.stand_depth
