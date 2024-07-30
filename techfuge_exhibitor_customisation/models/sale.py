# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext
import random
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_package_component_ids = fields.One2many("exhibitor.package.components", "sale_order_id",
                                                      string="Exhibitor Package Components")
    exhibitor_payment_stage_ids = fields.One2many("exhibitor.payment.stages", "sale_order_id",
                                                  string="Exhibitor Payment Stages")
    space_type_id = fields.Many2one("exhibitor.space.type", string="Space Type")
    total_area = fields.Float(string="Total Area (m2)", compute="_compute_total_area")
    rate_per_m2 = fields.Float(string="Rate per m2 ($)", compute="_compute_rate_per_m2")
    rate_per_m2_with_vat = fields.Float(string="Rate per m2 ($) + 5% VAT", compute="_compute_rate_per_m2")
    stall_dimensions = fields.Char(string="Stall Dimensions", compute="_compute_stall_dimensions")
    hall_ids = fields.Many2many("event.activity.location", string="Hall Number", domain=[('event_id', '!=', False)])
    stand_ids = fields.One2many("so.stand.details", "sale_order_id", string="Stand Details")
    agreement_sent = fields.Boolean(string="Agreement Sent")
    delivery_note = fields.Char(string="Delivery Note")
    other_reference = fields.Char(string="Other Reference(s)")
    buyer_order_no = fields.Char(string="Buyer's Order No.")
    buyer_order_date = fields.Datetime(string="Buyer's Order Date")
    dispatched_document_no = fields.Char(string="Dispatched Document No.")
    dispatched_through = fields.Char(string="Dispatched Through")
    destination = fields.Char(string="Destination")
    state = fields.Selection(selection_add=[
        ('quote_accepted', 'Quotation Accepted'),
        ('review_quote', 'Review Quote'),
        ('in_progress', 'Agreement in Progress'),
        ('sale', 'Sales Order')])
    component_amount_total = fields.Monetary('Component Total', compute='_compute_component_amount_total', store=True)
    enable_hotel_request = fields.Boolean(string="Enable Hotel Request")
    enable_shipment_section = fields.Boolean(string="Enable Shipment Section")
    enable_contractor_section = fields.Boolean(string="Enable Contractor Section")
    hotel_special_inclusion_info = fields.Html(string="Hotel Information")
    include_special_condition = fields.Boolean(string="Include Special")
    is_other_request = fields.Boolean(string="Other Request")
    exhibitor_other_request_comment = fields.Text(string="Comment for Other Request")
    brand_id = fields.Many2one('res.brand', string='Brand')
    reference_id = fields.Many2one('res.partner', string="Reference")
    note_text = fields.Text(string="Note Text", compute="_compute_note_text")
    so_type = fields.Selection([
        ('normal_quote', 'Normal Quote'),
        ('agreement', 'Agreement')
    ], string="SO Type", default="normal_quote")
    hotel_request_id = fields.Many2one("exhibitor.hotel.request", string="Hotel Request")
    agent_id = fields.Many2one("res.partner", string="Agent", related="partner_id.agent_id")
    total_discount = fields.Monetary("Total Discount", compute='_compute_total_discount')


    def get_bank_details(self):
        return  self.event_id.get_bank_details(self.partner_id)
    def change_invoice_sales(self):
        for rec in self.invoice_ids:
            rec.sale_id = self
            rec.event_id = self.event_id


    def get_other_information(self):
        if self.partner_id.country_id:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', self.partner_id.country_id.id), ('event_id', '=', self.event_id.id)])
            if not agreement_template_id:
                agreement_template_id = self.env['event.agreement.country'].search(
                    [('country_id', '=', False), ('event_id', '=', self.event_id.id)])


        else:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', False), ('event_id', '=', self.event_id.id)])
        return agreement_template_id.special_instruction
    def get_payement_instruction(self):
        if self.partner_id.country_id:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', self.partner_id.country_id.id), ('event_id', '=', self.event_id.id)])
            if not agreement_template_id:
                agreement_template_id = self.env['event.agreement.country'].search(
                    [('country_id', '=', False), ('event_id', '=', self.event_id.id)])


        else:
            agreement_template_id = self.env['event.agreement.country'].search(
                [('country_id', '=', False), ('event_id', '=', self.event_id.id)])
        return agreement_template_id.payment_instruction


    @api.depends('note')
    def _compute_note_text(self):
        for order in self:
            order.note_text = ''
            if order.note:
                order.note_text = html2plaintext(order.note)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.onchange_include_special_condition_section_2b()
        res.onchange_include_special_condition()
        res.check_payment_stage_validation()
        if res.so_type == 'agreement':
            if res.order_line[0] and res.total_area:
                if res.order_line[0].product_uom_qty != res.total_area:

                    raise ValidationError(_("The quantity and total area are not equal in order %s") % res.name)
            if res.hall_ids and not res.stand_ids:
                raise ValidationError(_("Please enter the stand details"))
        return res

    def write(self, vals):
        res = super().write(vals)
        self.check_payment_stage_validation()
        if self.so_type == 'agreement':
            if self.order_line[0] and self.total_area:
                if self.order_line[0].product_uom_qty != self.total_area:
                    raise ValidationError(_("The quantity and total area are not equal in order %s") % self.name)
            if self.hall_ids and not self.stand_ids:
                raise ValidationError(_("Please enter the stand details"))
        if self.space_type_id:
            if vals:
                if 'brand_id' in vals or 'reference_id' in vals:
                    if self.invoice_ids:
                        for invoice in self.invoice_ids:
                            if 'brand_id' in vals and vals['brand_id']:
                                invoice.brand_id = vals['brand_id']
                            if 'reference_id' in vals and vals['reference_id']:
                                invoice.reference_id = vals['reference_id']
            self.generate_exhibitor_contract()
        return res

    def check_payment_stage_validation(self):
        print(">>>")
        if self.exhibitor_payment_stage_ids:
            payment_stage_percentage_total = sum(self.exhibitor_payment_stage_ids.mapped('paid_percentage'))
            payment_stage_amount_total = sum(self.exhibitor_payment_stage_ids.mapped('paid_amount'))
            if payment_stage_percentage_total != 100:
                raise ValidationError(_("The percentage added in the payment stage is not equal to 100"))
            if payment_stage_amount_total != self.amount_total:
                raise ValidationError(
                    _("The amount added in the payment stage is not equal to the total amount of the quotation"))

    def action_quotation_send(self):
        res = super().action_quotation_send()
        if self.env.context.get('proforma'):
            mail_template = self.env.ref('techfuge_exhibitor_customisation.mail_template_sale_proforma_exhibitor')
        else:
            mail_template = self.env.ref('techfuge_exhibitor_customisation.mail_template_sale_quotation_exhibitor')
            if self.opportunity_id:
                self.opportunity_id.stage_id = self.env.ref('crm.stage_lead3').id
        res['context']['default_template_id'] = mail_template.id
        return res

    def send_exhibitor_agreement(self, from_action=False):
        mail_template = self.env.ref('techfuge_exhibitor_customisation.mail_template_sale_exhibitor_agreement')
        lang = self.env.context.get('lang')
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': True,
            'default_template_id': mail_template.id if mail_template else None,
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

    def generate_exhibitor_contract(self):
        if not self.space_type_id or not self.hall_ids:
            raise UserError(_("Please add the agreement details"))

        if self.event_id and self.agreement_sent:
            company_address = ''
            if self.partner_id.parent_id:
                if self.partner_id.parent_id.street:
                    company_address += self.partner_id.parent_id.street + ', '
                if self.partner_id.parent_id.city:
                    company_address += self.partner_id.parent_id.city + ', '
                if self.partner_id.parent_id.state_id:
                    company_address += self.partner_id.parent_id.state_id.name


            if self.exhibitor_contract_id:
                self.exhibitor_contract_id.commercial_items_ids.unlink()
                self.exhibitor_contract_id.stand_ids.unlink()
                self.exhibitor_contract_id.exhibitor_payment_stage_ids.unlink()

            commercial_items = []
            for line in self.order_line:
                commercial_items.append((0, 0, {
                    'product_template_id': line.product_template_id.id,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom_id': line.product_uom.id,
                    'price_unit': line.price_unit,
                    'tax_ids': line.tax_id.ids,
                    'price_subtotal': line.price_subtotal,
                    'price_tax': line.price_tax,
                    'price_total': line.price_total
                }))

            stand_details = []
            for stand in self.stand_ids:
                stand_details.append((0, 0, {
                    'stand_id': stand.stand_id.id,
                    'hall_id': stand.hall_id.id,
                    'stand_description': stand.stand_description,
                    'stand_width': stand.stand_width,
                    'stand_depth': stand.stand_depth,
                    'stand_size': stand.stand_size
                }))

            payment_stages = []
            for payment in self.exhibitor_payment_stage_ids:
                payment_stages.append((0, 0, {
                    'name': payment.name,
                    'payment_type': payment.payment_type,
                    'paid_percentage': payment.paid_percentage,
                    'paid_amount': payment.paid_amount,
                    'payment_due_date': payment.payment_due_date
                }))

            allowed_hotel_rooms = 0
            no_of_hotel_persons = 0
            eligible_for_food_coupon = True

            if not self.space_type_id.type == 'non-package':
                if self.total_area <= 72:
                    allowed_hotel_rooms = 1
                    no_of_hotel_persons = 2
                elif 72 < self.total_area <= 144:
                    allowed_hotel_rooms = 2
                    no_of_hotel_persons = 4
                elif self.total_area > 144:
                    allowed_hotel_rooms = 3
                    no_of_hotel_persons = 6

                eligible_for_food_coupon = False

            exhibitor_contract_vals = {
                'exhibitor_name': self.partner_id.name,
                'mobile': self.partner_id.mobile,
                'email': self.partner_id.additional_email,
                'landline': self.partner_id.phone,
                'company_name': self.partner_id.parent_id.name,
                'company_address': company_address,
                'country_name': self.partner_id.country_id.name if self.partner_id.country_id else '',
                'sale_order_id': self.id,
                'so_amount_total': self.amount_total,
                'commercial_items_ids': commercial_items,
                'stand_ids': stand_details,
                'exhibitor_payment_stage_ids': payment_stages,
                'event_id': self.event_id.id,
                'enable_hotel_request': self.enable_hotel_request,
                'enable_shipment_section': self.enable_shipment_section,
                'enable_contractor_section': self.enable_contractor_section,
                'total_area': self.total_area,
                'stall_dimensions': self.stall_dimensions,
                'partner_id': self.partner_id.id,
                'agent_id': self.partner_id.agent_id.id if self.partner_id.agent_id else False,
                'allowed_hotel_rooms': allowed_hotel_rooms,
                'no_of_hotel_persons': no_of_hotel_persons,
                'brand_id': self.brand_id.id if self.brand_id else False,
                'reference_id': self.reference_id.id if self.reference_id else False,
                'eligible_for_food_coupon': eligible_for_food_coupon,
                'branding_panel_width' : self.event_id.branding_panel_width,
            'branding_panel_height' :  self.event_id.branding_panel_height,
            'allowed_no_of_nights':self.event_id.allowed_no_of_nights
            }

            if not self.exhibitor_contract_id:
                exhibitor_contract = self.env['exhibitor.contract'].with_user(self.user_id.id).create(
                    exhibitor_contract_vals)
                self.exhibitor_contract_id = exhibitor_contract.id
                self.partner_id.exhibitor_contract_id = exhibitor_contract.id
                self.sudo().write({
                    'state': 'in_progress'
                })
            else:
                self.exhibitor_contract_id.update(exhibitor_contract_vals)

    @api.model
    def create_portal_user_for_exhibitor(self):
        """ For creating a portal user for the exhibitor"""

        res_users = self.env['res.users'].sudo()
        exhibitor_user = False
        if self.partner_id:
            user_password = self.generate_random_password()
            if self.partner_id.additional_email:
                partner_email = self.partner_id.additional_email
            else:
                partner_email = self.partner_id.email
            if self.brand_id:
                latest_user_id = res_users.search([], order='id desc')[0].id
                login = self.brand_id.name + str(latest_user_id + 1)
                if not res_users.search([('login', '=', login)]):
                    if partner_email:
                        exhibitor_user = res_users.with_context(create_exhibitor_user=True).create({
                            'name': self.partner_id.name,
                            'email': partner_email,
                            'login': login,
                            'password': user_password,
                            'partner_id': self.partner_id.id,
                            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                            'user_category': 'exhibitor',
                            'event_id': self.event_id.id,
                            'brand_id': self.brand_id.id if self.brand_id else False
                        })
                        self.opportunity_id.sudo().write({
                            'exhibitor_user_id': exhibitor_user.id,
                            'exhibitor_user_login': exhibitor_user.login,
                            'exhibitor_user_password': user_password,
                        })
        return exhibitor_user

    def generate_random_password(self):
        """ Returns random password string containing alphanumeric characters """

        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pw_length = 8
        password = ""
        for i in range(pw_length):
            next_index = random.randrange(len(alphabet))
            password = password + alphabet[next_index]
        return password

    def action_accept_quotation(self):
        self.action_confirm()

    def action_confirm(self):
        if self.so_type == 'normal_quote':
            res = super().action_confirm()
            return res

        else:
            res = super().action_confirm()
            user = self.user_id if self.user_id else self.env.ref('base.user_admin')
            if self.agreement_sent:
                if not self.partner_id.email:
                    raise ValidationError(_("Please add the email address of the customer"))
                if self.opportunity_id:
                    self.opportunity_id.action_set_won()
                return res
            elif self.env.context.get('is_other_request'):
                return res
            else:
                self.with_user(user.id).sudo().write({
                    'state': 'quote_accepted'
                })

    def action_view_exhibitor_contract(self):
        action = self.env['ir.actions.actions']._for_xml_id(
            'techfuge_exhibitor_customisation.action_view_exhibitor_contracts')
        form_view = [(self.env.ref('techfuge_exhibitor_customisation.view_exhibitor_contract_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.exhibitor_contract_id.id
        return action

    def get_total_tax_text(self):
       print(">>>>>>get_total_tax_text")
       if self.amount_tax:
            tax = self.amount_tax / self.amount_untaxed
       else:
           tax = 0
       return str(tax*100)+" % "

    def is_zero_total_tax_text(self):
        if self.amount_tax:
            tax = self.amount_tax / self.amount_untaxed
        else:
            tax = 0
        return tax == 0

    @api.depends('stand_ids')
    def _compute_total_area(self):
        for order in self:
            order.total_area = float("{:.2f}".format(sum(order.stand_ids.mapped('stand_size'))))

    @api.depends('order_line.tax_id', 'order_line.price_unit')
    def _compute_rate_per_m2(self):
        for order in self:
            order.rate_per_m2 = 0
            order.rate_per_m2_with_vat = 0
            order.rate_per_m2_with_vat = ''
            if order.order_line and order.space_type_id:
                unit_price = order.order_line.mapped('price_unit')[0]
                if order.order_line.tax_id:
                    tax_id = order.order_line.tax_id[0]
                    if tax_id.price_include:
                        order.rate_per_m2 = unit_price - (unit_price / 21)
                        order.rate_per_m2_with_vat = unit_price
                    else:
                        order.rate_per_m2 = unit_price
                        if order.amount_untaxed == 0:
                            tax_persentage = 0
                        else:
                            tax_persentage =  order.amount_tax/order.amount_untaxed
                        order.rate_per_m2_with_vat = unit_price + (unit_price * tax_persentage)

    @api.depends('stand_ids')
    def _compute_stall_dimensions(self):
        for order in self:
            order.stall_dimensions = ''
            if order.order_line:
                total_stand_width = float("{:.2f}".format(sum(order.stand_ids.mapped('stand_width'))))
                total_stand_depth = float("{:.2f}".format(sum(order.stand_ids.mapped('stand_depth'))))
                width = str(total_stand_width)
                depth = str(total_stand_depth)
                order.stall_dimensions = width + ' x ' + depth

    @api.depends('exhibitor_package_component_ids')
    def _compute_component_amount_total(self):
        for order in self:
            component_lines = order.exhibitor_package_component_ids
            currency = order.pricelist_id.currency_id or self.env.company.currency_id
            order.component_amount_total = currency.round(sum(component_lines.mapped('total_price')))


    def _create_invoices(self, grouped=False, final=False, date=None):
        """ Override to add components and payment stages """
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        if invoices:
            for order in self:
                if order.brand_id:
                    invoices.write({
                        'brand_id': order.brand_id.id
                    })
                if order.reference_id:
                    invoices.write({
                        'reference_id': order.reference_id.id
                    })
                if order.exhibitor_package_component_ids:
                    invoices.write({
                        'exhibitor_package_component_ids': order.exhibitor_package_component_ids.ids
                    })
                if order.exhibitor_payment_stage_ids:
                    invoices.write({
                        'exhibitor_payment_stage_ids': order.exhibitor_payment_stage_ids.ids
                    })
        return invoices

    def action_update_quotation_brand_and_reference(self):
        for order in self:
            if order.partner_id:
                order.write({'partner_id': order.opportunity_id.partner_id.id})
            if order.exhibitor_contract_id:
                order.exhibitor_contract_id.partner_id = order.opportunity_id.partner_id
                order.exhibitor_contract_id.company_name = order.opportunity_id.partner_name
                order.exhibitor_contract_id.company_address=  order.opportunity_id.street
            if order.opportunity_id:
                if not order.brand_id:
                    if order.opportunity_id.brand_id:
                        order.write({'brand_id': order.opportunity_id.brand_id.id})
                if not order.reference_id:
                    if order.opportunity_id.reference_id:
                        order.write({'reference_id': order.opportunity_id.reference_id.id})

    @api.depends('order_line.discount_amount')
    def _compute_total_discount(self):
        for order in self:
            total_discount = sum(line.discount_amount for line in order.order_line)
            order.total_discount = total_discount


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    agent_id = fields.Many2one('res.partner', string="Agent", related="order_id.agent_id", store=True)
    brand_id = fields.Many2one('res.brand', string="Brand", related="order_id.brand_id", store=True)
    reference_id = fields.Many2one('res.partner', string="Reference", related="order_id.reference_id", store=True)
    order_type = fields.Selection(string="SO Type", related="order_id.so_type", store=True)
    order_invoiced_amount = fields.Monetary(string="Invoiced Amount", currency_field='currency_id',
                                            compute="_compute_order_invoiced_and_paid_amount", store=True)
    order_paid_amount = fields.Monetary(string="Paid Amount", currency_field='currency_id',
                                        compute="_compute_order_invoiced_and_paid_amount", store=True)
    discount_amount = fields.Monetary(string="Discount Amount", compute='_compute_discount_amount')

    hall_ids = fields.Many2many(related='order_id.hall_ids',string='Hall')
    stand_ids = fields.Char(compute="_compute_stands_details")
    exhibitor_comments = fields.Text(related='order_id.exhibitor_other_request_comment')


    def action_view_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.order_id.name,
            'view_mode': 'form',
            'res_model': 'sale.order',
            'target': 'current',
            'res_id': self.order_id.id,
        }

    @api.depends('order_id')
    def _compute_stands_details(self):
        for rec in self:
            if rec.order_id.stand_ids:
                rec.stand_ids =', '.join(rec.order_id.stand_ids.mapped('stand_number'))
            else:
                rec.stand_ids = ''



    @api.depends('order_id')
    def _compute_order_invoiced_and_paid_amount(self):
        for line in self:
            line.order_invoiced_amount = 0
            line.order_paid_amount = 0
            invoices = self.env['account.move'].search([('sale_id', '=', line.order_id.id)])
            if invoices:
                for invoice in invoices:
                    payments = self.env['account.payment'].search([('ref', '=', invoice.name)])
                    if payments:
                        line.order_paid_amount = sum(payments.mapped('amount'))
                line.order_invoiced_amount = sum(invoices.mapped('amount_total'))

    @api.depends('discount')
    def _compute_discount_amount(self):
        for line in self:
            discount_amount = ((line.product_uom_qty * line.price_unit) * line.discount) / 100
            line.discount_amount = discount_amount
