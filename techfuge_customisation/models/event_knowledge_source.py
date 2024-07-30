# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventKnowledgeSource(models.Model):
    _name = 'event.knowledge.source'
    _description = 'Event Knowledge Source'

    name = fields.Char(string='Name')
