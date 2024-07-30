
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_golf = fields.Boolean(string="Is Golf Club")
