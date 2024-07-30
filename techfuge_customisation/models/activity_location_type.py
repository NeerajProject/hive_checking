# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ActivityLocationType(models.Model):
    _name = 'activity.location.type'
    _description = 'Activity Location Type'

    name = fields.Char(string='Name')
    attendee_group_id = fields.Many2one('event.attendee.group', string='Group')
    is_cafe = fields.Boolean(string='Is Cafe')
