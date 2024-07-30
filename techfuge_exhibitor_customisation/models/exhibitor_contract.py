# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError




class ExhibitorContract(models.Model):
    _name = 'exhibitor.contract'
    _description = 'Exhibitor Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    is_submited_hotel_request = fields.Boolean(default=True)

    active = fields.Boolean(default=True)
    is_readonly_shipping = fields.Boolean(string="Is Readonly Shipping")
    maximum_hotel_booking_delete = fields.Float(default=2,string="Number of Delete ")
    attendee_registration_link = fields.Char(compute = "_compute_attendee_url")
    authentication_token = fields.Char(compute="_compute_authentication_token",store=True)

    def _compute_authentication_token(self):
        for rec in self:
            rec.authentication_token = hash(rec.name)
    def _compute_attendee_url(self):
        for rec in self:
            rec.attendee_registration_link = rec.get_base_url()+"/create/exhibitor/attendee?token="+str(rec.authentication_token)


    # def write(self, vals):
    #     result = super(ExhibitorContract, self).write(vals)
    #     mail_template = self.env.ref('email_templates_for_portals.email_template_submission_of_email')
    #     mail_template.send_mail(result.id, force_send=True)
    #     return result    # def write(self, vals):
    #     result = super(ExhibitorContract, self).write(vals)
    #     mail_template = self.env.ref('email_templates_for_portals.email_template_submission_of_email')
    #     mail_template.send_mail(result.id, force_send=True)
    #     return result

    def action_send_exhibitor_registration_mails(self):
        if self.sale_order_id.opportunity_id:
            user = self.env.ref('base.user_admin')

            lead_id = self.sale_order_id.opportunity_id
            mail_template = self.env.ref(
                'techfuge_customisation.email_template_exhibitor_registration_confirmed_mail'
            )
            mail_template.with_user(user.id).sudo().with_context(
                partner_full_name=self.partner_id.name).send_mail(lead_id.id, force_send=True)

    def warning_message_for_booking_block(self):
        for rec in self.hotel_request_ids:
            if not rec.upload_voucher:
                return True
        return False
    @api.onchange('brand_id')
    def change_brand_ids(self):
        if self.sale_order_id.opportunity_id:
            self.sale_order_id.opportunity_id.brand_id = self.brand_id.id
            self.sale_order_id.action_update_quotation_brand_and_reference()

    def _is_hotel_booking_day_is_over(self):
        if self.event_id.last_booking_hotel:
            return  self.event_id.last_booking_hotel >  fields.Date.today()
        else:
            return  False
    @api.depends('hotel_request_ids')
    def _is_voucher_is_uploaded(self):
        submit =True
        for rec in self.hotel_request_ids:
            if rec.upload_voucher:
                submit = False
                break

        self.is_submited_hotel_request = submit



    def get_allowed_number_of_night(self):
        return '10'
    def get_booked_rooms(self):
        room = self.hotel_request_ids.mapped('room_id')


        return len(list( set(room)))
    def check_is_already_exist(self,room):
        return  len(self.hotel_request_ids.filtered(lambda rec: rec.room_id in [room])) < 2
    def get_available_room(self):
        available_room =[]
        number_list={
            1: "first",
            2: "second",
            3: "third",
            4: "fourth",
            5: "fifth",
            6: "sixth",
            7: "seventh",
            8: "eighth",
            9: "ninth",
            10: "tenth",
            11: "eleventh",
            12: "twelfth",
            13: "thirteenth",
            14: "fourteenth",
            15: "fifteenth",
            16: "sixteenth",
            17: "seventeenth",
            18: "eighteenth",
            19: "nineteenth",
            20: "twentieth",
            21: "twenty-first",
            22: "twenty-second",
            23: "twenty-third",
            24: "twenty-fourth",
            25: "twenty-fifth"
            # Add more mappings if needed
        }

        for rec in range(1,self.allowed_hotel_rooms+1):
            print(rec)
            if self.check_is_already_exist(number_list[rec].upper()):
                available_room.append(number_list[rec].upper())
        return  available_room


    name = fields.Char(string='Name', default=lambda self: _('New'), readonly=True)
    exhibitor_name = fields.Char(string="Exhibitor Name", readonly=True)
    title = fields.Selection(selection=[
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
    ], string='Title', readonly=True)
    first_name = fields.Char(string="First Name", readonly=True)
    last_name = fields.Char(string="Last Name", readonly=True)
    mobile = fields.Char(string="Mobile", readonly=True)
    landline = fields.Char(string="Landline", readonly=True)
    email = fields.Char(string="Email", readonly=True)
    company_name = fields.Char(string="Company Name", readonly=True,tracking=True)
    company_address = fields.Char(string="Company Address", readonly=True,tracking=True)
    country_name = fields.Char(string="Country", readonly=True,tracking=True)
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", readonly=True)
    sale_order_state = fields.Selection(related="sale_order_id.state", string="Order Status")
    lead_state = fields.Many2one("crm.stage", related="sale_order_id.opportunity_id.stage_id", string="Lead Status")
    space_type_id = fields.Many2one("exhibitor.space.type", string="Space Type", related="sale_order_id.space_type_id",
                                    store=True)
    so_amount_untaxed = fields.Monetary(string="Order Amount Untaxed", related="sale_order_id.amount_untaxed",
                                        readonly=True)
    so_amount_tax = fields.Monetary(string="Order Amount Tax", related="sale_order_id.amount_tax", readonly=True)
    so_amount_total = fields.Monetary(string="Order Amount Total", readonly=True)
    invoice_amount_total = fields.Monetary(string="Total Invoice Amount", compute="_compute_total_invoice_payments")
    payment_amount_total = fields.Monetary(string="Total Payments", compute="_compute_total_invoice_payments")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, readonly=True)
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', readonly=True,tracking=True)
    event_id = fields.Many2one("event.event", string="Event", readonly=True,tracking=True)
    no_of_stands = fields.Integer(string="No. of Stands", compute="_compute_no_of_stands", readonly=False,tracking=True)
    no_of_badges = fields.Integer(string="Badge Count",tracking=True)
    allowed_hotel_rooms = fields.Integer(string="Allowed Hotel Rooms",tracking=True)
    no_of_hotel_persons = fields.Integer(string="No. of Persons in a Room",tracking=True)
    enable_hotel_request = fields.Boolean(string="Enable Hotel Request",tracking=True)
    allowed_no_of_nights = fields.Integer(string="Allowed No. of Nights",tracking=True)
    enable_shipment_section = fields.Boolean(string="Enable Shipment Section",tracking=True)
    enable_contractor_section = fields.Boolean(string="Enable Contractor Section",tracking=True)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts')
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts')
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    stand_ids = fields.One2many("contract.stand.details", "exhibitor_contract_id", string="Stand Details")
    total_area = fields.Float(string="Total Area (m2)")
    stall_dimensions = fields.Char(string="Stall Dimensions",tracking=True)
    hall_number = fields.Char(string="Hall Number", compute='_compute_hall_number')
    commercial_items_ids = fields.One2many("exhibitor.commercial.items", "exhibitor_contract_id",
                                           string="Commercial Items",tracking=True)
    badge_ids = fields.One2many("event.registration", "exhibitor_contract_id", tracking=True,string="Badge Details")
    invitation_letter_request_ids = fields.One2many("exhibitor.invitation.letter.request", "exhibitor_contract_id",
                                                    string="Invitation Letter Requests",tracking=True)
    hotel_request_ids = fields.One2many("exhibitor.hotel.request", "exhibitor_contract_id", string="Hotel Requests",tracking=True)
    exceeding_charges = fields.Integer(string="Exceeding Volume Charges / CBM", default=100)
    exhibitor_user_id = fields.Many2one("res.users", "Exhibitor User")
    shipment_detail_ids = fields.One2many("exhibitor.shipment.details", "exhibitor_contract_id",
                                          string="Shipment Details",tracking=True)
    shipment_document_ids = fields.One2many("shipment.uploaded.documents", "exhibitor_contract_id",
                                            string="Shipment Uploaded Documents")
    uploaded_document_ids = fields.One2many("exhibitor.uploaded.documents", "exhibitor_contract_id",
                                            string="Uploaded Documents")
    contractor_ids = fields.One2many("exhibitor.contractor.details", "exhibitor_contract_id",
                                     string="Contractor Details")
    contractor_document_ids = fields.One2many("contractor.uploaded.documents", "exhibitor_contract_id",
                                              string="Contractor Uploaded Documents")
    exhibitor_payment_stage_ids = fields.One2many("exhibitor.payment.stages", "exhibitor_contract_id",
                                                  string="Exhibitor Payment Stages")
    other_request_ids = fields.One2many("exhibitor.other.request", "exhibitor_contract_id",
                                        string="Other Requests")
    exhibitor_sale_order_count = fields.Integer(string='Sale Order Count', store=False, readonly=True,
                                                compute='_compute_exhibitor_sale_order_count')
    exhibitor_other_request_count = fields.Integer(string='Other Request Count', store=False, readonly=True,
                                                   compute='_compute_exhibitor_other_request_count')
    exhibitor_invoice_count = fields.Integer(string='Invoice Count', store=False, readonly=True,
                                             compute='_compute_exhibitor_invoice_count')
    exhibitor_payments_count = fields.Integer(string='Payments Count', store=False, readonly=True,
                                              compute='_compute_exhibitor_payments_count')
    contractor_details_count = fields.Integer(string='Contractor Count', store=False, readonly=True,
                                              compute='_compute_contractor_details_count')
    brand_id = fields.Many2one('res.brand', string='Brand',tracking=True)
    reference_id = fields.Many2one('res.partner', string="Reference")
    eligible_for_food_coupon = fields.Boolean(string="Eligible for Food Coupon")
    no_of_food_coupons = fields.Integer(string="No. of Food Coupons")
    used_food_coupons = fields.Integer(string="Used Food Coupons")
    remaining_food_coupons = fields.Integer(string="Remaining Food Coupons", compute="_compute_remaining_food_coupons")
    enable_finance_section = fields.Boolean(string="Enable Finance Section", default=True)
    dashboard_access = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('granted', 'Granted'),
    ], string='Dashboard Access', default="pending", compute="_compute_dashboard_access")
    agent_id = fields.Many2one("res.partner", string="Agent", related="partner_id.agent_id")
    allow_edit_commercials = fields.Boolean(string="Allow Edit Commercials", compute='_compute_allow_edit_commercials')

    






    def get_first_and_last_room_for_notfication(self):
        if self.hotel_request_ids:
            return len(self.hotel_request_ids) < self.allowed_hotel_rooms*2
        else:
            return False
    def get_available_room_number(self):
        return  self.room_ids.filtered(lambda act: act.count >1)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code('exhibitor.contract') or _("New")
        return super(ExhibitorContract, self).create(vals_list)

    @api.depends('commercial_items_ids.price_subtotal', 'commercial_items_ids.price_tax',
                 'commercial_items_ids.price_total')
    def _compute_amounts(self):
        for contract in self:
            commercial_item_lines = contract.commercial_items_ids
            contract.amount_untaxed = sum(commercial_item_lines.mapped('price_subtotal'))
            contract.amount_total = sum(commercial_item_lines.mapped('price_total'))
            contract.amount_tax = sum(commercial_item_lines.mapped('price_tax'))

    def _compute_tax_totals(self):
        for contract in self:
            order_lines = contract.sale_order_id.order_line.filtered(lambda x: not x.display_type)
            contract.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                contract.sale_order_id.currency_id or contract.sale_order_id.company_id.currency_id,
            )

    def write(self, vals):
        res = super().write(vals)
        if self.no_of_stands and self.stand_ids:
            if len(self.stand_ids) > self.no_of_stands:
                raise ValidationError(_("You cannot add more stands than the defined number of stands"))
        return res

    @api.depends('stand_ids')
    def _compute_no_of_stands(self):
        for contract in self:
            if contract.stand_ids:
                contract.no_of_stands = len(contract.stand_ids)

    @api.model
    def get_badge_information(self, user_id):
        badge_data = {}
        if user_id:
            user = self.env['res.users'].sudo().browse(int(user_id))
            if user:
                contract = False
                if user.user_category == 'exhibitor':
                    contract = self.env['exhibitor.contract'].sudo().search([
                        ('partner_id', '=', user.partner_id.id)
                    ], limit=1)
                elif user.user_category == 'contractor':
                    contract = self.env['exhibitor.contractor.details'].sudo().search([
                        ('partner_id', '=', user.partner_id.id)
                    ], limit=1)
                if contract:
                    used_badges = len(contract.badge_ids)
                    remaining_badges = 0
                    if contract.no_of_badges:
                        remaining_badges = contract.no_of_badges - used_badges
                    badge_data.update({
                        'used_badges': used_badges,
                        'remaining_badges': remaining_badges,
                    })
        return badge_data

    def action_view_exhibitor_sale_orders(self):
        self.ensure_one()

        action = {
            'name': _("Sale Orders"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }
        sale_orders = self.env['sale.order'].search(
            [('partner_id', '=', self.partner_id.id), ('event_id', '=', self.event_id.id)])
        sale_order_ids = sale_orders.ids
        if len(sale_order_ids) == 1:
            sale_order = sale_order_ids[0]
            action['res_id'] = sale_order
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', sale_order_ids)]
        return action

    def _compute_exhibitor_sale_order_count(self):
        for contract in self:
            sale_orders = self.env['sale.order'].search(
                [('partner_id', '=', contract.partner_id.id), ('event_id', '=', contract.event_id.id)])
            contract.exhibitor_sale_order_count = len(sale_orders)

    def action_view_exhibitor_other_requests(self):
        self.ensure_one()

        action = {
            'name': _("Sale Orders"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }

        other_requests = self.env['sale.order'].search(
            [('partner_id', '=', self.partner_id.id), ('event_id', '=', self.event_id.id),
             ('is_other_request', '=', True)])
        other_request_ids = other_requests.ids

        if len(other_request_ids) == 1:
            other_request = other_request_ids[0]
            action['res_id'] = other_request
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', other_request_ids)]
        return action

    def _compute_exhibitor_other_request_count(self):
        for contract in self:
            other_requests = self.env['sale.order'].search(
                [('partner_id', '=', contract.partner_id.id), ('event_id', '=', contract.event_id.id),
                 ('is_other_request', '=', True)])
            contract.exhibitor_other_request_count = len(other_requests)

    def action_view_exhibitor_invoices(self):
        self.ensure_one()

        action = {
            'name': _("Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'target': 'current',
        }

        invoices = self.env['account.move'].search(
            [('partner_id', '=', self.partner_id.id), ('event_id', '=', self.event_id.id)])
        invoice_ids = invoices.ids

        if len(invoice_ids) == 1:
            invoice = invoice_ids[0]
            action['res_id'] = invoice
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', invoice_ids)]
        return action

    def _compute_exhibitor_invoice_count(self):
        for contract in self:
            invoices = self.env['account.move'].search(
                [('partner_id', '=', contract.partner_id.id), ('event_id', '=', contract.event_id.id)])
            contract.exhibitor_invoice_count = len(invoices)

    def action_view_exhibitor_payments(self):
        self.ensure_one()

        action = {
            'name': _("Payments"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'target': 'current',
        }

        payments = self.env['account.payment'].search(
            ['|', ('partner_id', '=', self.partner_id.parent_id.id), ('partner_id', '=', self.partner_id.id)])
        payment_ids = payments.ids

        if len(payment_ids) == 1:
            payment = payment_ids[0]
            action['res_id'] = payment
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', payment_ids)]
        return action

    def _compute_exhibitor_payments_count(self):
        for contract in self:
            payments = self.env['account.payment'].search(
                ['|', ('partner_id', '=', contract.partner_id.parent_id.id),
                 ('partner_id', '=', contract.partner_id.id)])
            contract.exhibitor_payments_count = len(payments)

    def action_view_contractor_details(self):
        self.ensure_one()

        action = {
            'name': _("Contractor Details"),
            'type': 'ir.actions.act_window',
            'res_model': 'exhibitor.contractor.details',
            'target': 'current',
        }

        contractors = self.env['exhibitor.contractor.details'].search([('exhibitor_contract_id', '=', self.id)])
        contractor_details_ids = contractors.ids

        if len(contractor_details_ids) == 1:
            contractor = contractor_details_ids[0]
            action['res_id'] = contractor
            action['view_mode'] = 'form'
            action['views'] = [(
                self.env.ref('techfuge_exhibitor_customisation.view_exhibitor_contractor_details_form').id, 'form'
            )]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', contractor_details_ids)]
        return action

    def _compute_contractor_details_count(self):
        for contract in self:
            contractors = self.env['exhibitor.contractor.details'].search([('exhibitor_contract_id', '=', self.id)])
            contract.contractor_details_count = len(contractors)

    @api.depends('no_of_food_coupons', 'used_food_coupons')
    def _compute_remaining_food_coupons(self):
        for contract in self:
            if contract.no_of_food_coupons and contract.used_food_coupons:
                contract.remaining_food_coupons = contract.no_of_food_coupons - contract.used_food_coupons
            else:
                contract.remaining_food_coupons = contract.no_of_food_coupons

    @api.depends('stand_ids')
    def _compute_hall_number(self):
        for contract in self:
            contract.hall_number = False
            if contract.stand_ids:
                contract.hall_number = contract.stand_ids[0].hall_id.name

    @api.depends('sale_order_id')
    def _compute_total_invoice_payments(self):
        for contract in self:
            contract.invoice_amount_total = 0
            contract.payment_amount_total = 0
            payments = self.env['account.payment'].search([
                '|',
                ('partner_id', '=', contract.partner_id.parent_id.id),
                ('partner_id', '=', contract.partner_id.id)
            ])
            if contract.sale_order_id:
                contract.invoice_amount_total = sum(contract.sale_order_id.invoice_ids.mapped('amount_total'))
                contract.payment_amount_total = sum(payments.mapped('amount'))

    def _compute_dashboard_access(self):
        for contract in self:
            contract.dashboard_access = 'pending'
            if contract.exhibitor_user_id:
                contract.dashboard_access = 'granted'

    def grant_portal_access_to_exhibitor(self):
        for contract in self.filtered(lambda c: c.dashboard_access == 'pending'):
            if contract.sale_order_id.opportunity_id:
                if contract.sale_order_id.opportunity_id.stage_id.is_won:
                    if not contract.exhibitor_user_id:
                        exhibitor_user = contract.sale_order_id.create_portal_user_for_exhibitor()
                        if exhibitor_user:
                            contract.exhibitor_user_id = exhibitor_user.id
                            exhibitor_user.hall_ids = contract.sale_order_id.hall_ids.ids
                            stand_ids = []
                            for stand in contract.sale_order_id.stand_ids:
                                if stand.stand_id.id not in stand_ids:
                                    stand_ids.append(stand.stand_id.id)
                            exhibitor_user.stand_ids = stand_ids
                            self.exhibitor_user_id = exhibitor_user.id
                            user = self.env.ref('base.user_admin')
                            if contract.sale_order_id.opportunity_id:
                                lead_id = contract.sale_order_id.opportunity_id
                                mail_template = self.env.ref(
                                    'techfuge_customisation.email_template_exhibitor_registration_confirmed_mail'
                                )
                                mail_template.with_user(user.id).sudo().with_context(
                                    partner_full_name=contract.partner_id.name).send_mail(lead_id.id, force_send=True)

    @api.onchange('enable_hotel_request')
    def onchange_enable_hotel_request(self):
        if self.enable_hotel_request and self.event_id:
            self.allowed_no_of_nights = self.event_id.allowed_no_of_nights

    def download_all_uploaded_documents(self):
        attachments = []
        for document in self.uploaded_document_ids:
            attachments.append(document.document_attachment_id.id)
        url = '/web/binary/download_multiple_attachments?res_model=exhibitor.contract&res_id=%s&attachments=%s' % (
            self.id, attachments)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def download_all_shipment_document(self):
        print("sbhdfjb")
        attachments = []
        for document in self.shipment_document_ids:
            if document.document_attachment_id:
                attachments.append(document.document_attachment_id.id)

        print(attachments)
        url = '/web/binary/download_multiple_attachments?res_model=exhibitor.contract&res_id=%s&attachments=%s' % (
            self.id, attachments)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    def download_all_contractor_documents(self):
        print(">>>>>>>>>>>>>>> download_all_contractor_documents")
        attachments = []
        for document in self.contractor_document_ids:
            print(">>>>>>>>>>>> d",document)
            attachments.append(document.document_attachment_id.id)
        print(attachments)
        url = '/web/binary/download_multiple_attachments?res_model=exhibitor.contract&res_id=%s&attachments=%s' % (
            self.id, attachments)

        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def _compute_allow_edit_commercials(self):
        for contract in self:
            contract.allow_edit_commercials = False
            if self.env.user.has_group('techfuge_exhibitor_customisation.group_edit_exhibitor_contract_commercials'):
                contract.allow_edit_commercials = True

