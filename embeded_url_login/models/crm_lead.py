from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command

class CrmLead(models.Model):
    _inherit = "crm.lead"
    exhibitor_user_id = fields.Many2one('res.users',copy=False)


