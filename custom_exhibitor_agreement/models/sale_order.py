from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_exihibitor_mail = fields.Boolean(default=False)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    include_special_condition_section_b = fields.Boolean(default=False,string="Include Section B")
    special_section_b = fields.Html()

    booth_rate_per_sqm = fields.Float()
    booth_rate_per_sqm_vat = fields.Float()

    total_unit_price = fields.Float(compute="_compute_total_unit_price")





    @api.onchange('include_special_condition')
    def onchange_include_special_condition(self):
        print(self.event_id.read())
        if self.include_special_condition:
            self.hotel_special_inclusion_info = self.event_id.special_include

    @api.onchange('include_special_condition_section_b')
    def onchange_include_special_condition_section_2b(self):
        print(">>>>>>>>",self.event_id.read())
        if self.include_special_condition_section_b:

            self.special_section_b = self.event_id.special_include_part_b
    @api.depends('order_line')
    def _compute_total_unit_price(self):
        total =0
        for rec in self.order_line:
            if rec.tax_id.price_include:
                total += rec.price_unit*(100/(100+rec.tax_id.amount))
            else:
                total +=rec.price_unit
        self.total_unit_price = total


    def  is_new_payment_template(self):

        if self.partner_id.country_id:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', self.partner_id.country_id.id), ('event_id', '=', self.event_id.id)])
            if not agreement_template_id:
                agreement_template_id = self.env['event.agreement.country'].search(
                    [('country_id', '=', False), ('event_id', '=', self.event_id.id)])


        else:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', False), ('event_id', '=', self.event_id.id)])
        return agreement_template_id.different_payment_description
    def action_generate_agreement(self):

        if self.partner_id.country_id:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', self.partner_id.country_id.id), ('event_id', '=', self.event_id.id)])
            if not agreement_template_id:
                agreement_template_id = self.env['event.agreement.country'].search(
                    [('country_id', '=', False), ('event_id', '=', self.event_id.id)])


        else:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', False), ('event_id', '=', self.event_id.id)])
        return agreement_template_id.email_template_id.report_template.report_action(self)
    def send_exhibitor_agreement(self, from_action=False):

        if self.partner_id.country_id:
            agreement_template_id = self.env['event.agreement.country'].search([('country_id','=',self.partner_id.country_id.id),('event_id','=',self.event_id.id)])
            if not agreement_template_id:
                agreement_template_id = self.env['event.agreement.country'].search(
                    [('country_id', '=', False), ('event_id', '=', self.event_id.id)])


        else:
            agreement_template_id = self.env['event.agreement.country'].search([('country_id', '=', False),('event_id','=',self.event_id.id)])


        mail_template = self.event_id.exhibitor_email_template_id
        lang = self.env.context.get('lang')
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': True,
            'default_template_id': agreement_template_id.email_template_id.id if agreement_template_id.email_template_id else None,
            'default_composition_mode': 'comment',
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
            'default_email_layout_xmlid': 'techfuge_exhibitor_customisation.mail_notification_layout_exhibitor_agreement',
            'is_exhibitor_agreement': True,
            'is_called_from_action': from_action
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
