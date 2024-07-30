# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import html2plaintext


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'
    is_place_order = fields.Boolean(string="Is place order")


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_place_order_invoice = fields.Boolean(default=False)
    exhibitor_package_component_ids = fields.One2many("exhibitor.package.components", "move_id",
                                                      string="Exhibitor Package Components")
    exhibitor_payment_stage_ids = fields.One2many("exhibitor.payment.stages", "move_id",
                                                  string="Exhibitor Payment Stages")
    narration_text = fields.Text(string="Note Text", compute="_compute_narration_text")
    invoice_payment_terms = fields.Html(string="Invoice Payment Terms")
    brand_id = fields.Many2one('res.brand', string='Brand')
    reference_id = fields.Many2one('res.partner', string="Lead Reference")
    place_order_comments = fields.Text(related="sale_id.exhibitor_other_request_comment")
    @api.depends('narration')
    def _compute_narration_text(self):
        for move in self:
            move.narration_text = ''
            if move.narration:
                move.narration_text = html2plaintext(move.narration)

    def action_invoice_sent(self):
        res = super().action_invoice_sent()
        mail_template = self.env.ref('techfuge_exhibitor_customisation.mail_template_send_invoice_exhibitor')
        res['context']['default_template_id'] = mail_template.id
        return res
    def get_bank_details(self):
        print(self.event_id.get_bank_details(self.partner_id))
        return self.event_id.get_bank_details(self.partner_id)