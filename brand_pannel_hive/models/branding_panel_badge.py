from odoo import fields, models, api


class BrandingPanelBadge(models.Model):
    _name = 'branding.panel.badge'
    _description = 'Description'

    name = fields.Char()
    country_id = fields.Many2one('res.country')
    event_id = fields.Many2one('event.event')
    background_image =  fields.Binary(string="Branding Panel Portal(384px x 846px)", attachment=True, store=True)
    background_image_report =  fields.Binary(string="Branding Panel Report (871px X 1920px)", attachment=True, store=True)








class EventEvent(models.Model):
    _inherit = 'event.event'

    branding_panel_background_id = fields.One2many('branding.panel.badge','event_id')

    branding_panel_width = fields.Float()
    branding_panel_height = fields.Float()
