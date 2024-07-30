# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorShipmentDetails(models.Model):
    _name = 'exhibitor.shipment.details'
    _description = 'Exhibitor Shipment Details'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_name = fields.Char(string="Exhibitor Name", related="exhibitor_contract_id.exhibitor_name")
    event_id = fields.Many2one("event.event", string="Event")
    total_shipment_volume = fields.Float(string="Total Shipment Volume")
    allowed_cbm = fields.Float(string="Allowed CBM / 10 SQM")
    extra_cbm = fields.Float(string="Extra CBM")
    exceeding_charges = fields.Integer(string="Exceeding Volume Charges / CBM")
    additional_charges = fields.Float(string="Additional Charges")
    final_charges = fields.Float(string="Final Charges")
    no_of_cartons = fields.Integer(string="No of Cartons")
    net_weight = fields.Float(string="Net Weight")
    gross_weight = fields.Float(string="Gross Weight")
    port_of_loading = fields.Char(string="Name of Port of Loading")
    port_of_arrival_in_uae = fields.Char(string="Port of Arrival in UAE")
    shipment_status = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('approve_with_charges', 'Approve with Charges'),
        ('approve_without_charges', 'Approve without Charges'),
    ], string="Status", default="pending")
