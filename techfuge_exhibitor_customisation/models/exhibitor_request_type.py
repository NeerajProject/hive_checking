# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ExhibitorRequestType(models.Model):
    _name = 'exhibitor.request.type'
    _description = 'Exhibitor Request Type'

    name = fields.Char(string='Name')
