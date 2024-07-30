from odoo import api, fields, models
from odoo.tools import html2plaintext


class AccountMove(models.Model):
    _inherit = 'product.template'

    is_place_order = fields.Boolean(string="Is Place Order")