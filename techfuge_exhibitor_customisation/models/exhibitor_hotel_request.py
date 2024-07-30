# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExhibitorHotelRequest(models.Model):
    _name = 'exhibitor.hotel.request'
    _description = 'Exhibitor Hotel Request'
    _rec_name = 'attendee_full_name'

    room_id = fields.Char(string="room")
    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    company_name = fields.Char(string="Company Name", related="exhibitor_contract_id.company_name")
    brand_id = fields.Many2one("res.brand", string="Brand", related="exhibitor_contract_id.brand_id")
    reference_id = fields.Many2one("res.partner", string="Reference", related="exhibitor_contract_id.reference_id")
    attendee_id = fields.Many2one("event.registration", string="Attendee")
    event_id = fields.Many2one("event.event", string="Event")
    attendee_full_name = fields.Char(string="Attendee Name", related="attendee_id.attendee_full_name")
    hotel_name = fields.Char(string="Hotel Name")
    hotel_booking_ref = fields.Char(string="Booking Reference No.")
    no_of_rooms = fields.Integer(string="No. of Rooms")
    checkin_date = fields.Date(string="Check In Date")
    checkout_date = fields.Date(string="Check Out Date")
    no_of_nights = fields.Integer(string="No. of Nights", compute="_compute_number_of_nights")
    allowed_no_of_nights = fields.Integer(string="Allowed No. of Nights",
                                          related="exhibitor_contract_id.allowed_no_of_nights")
    additional_no_of_nights = fields.Integer(string="Additional No. of Nights")
    additional_paid_amount = fields.Integer(string="Additional Payment")
    booking_status = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], string="Booking Status", default="pending")
    upload_voucher = fields.Binary(string="Upload Voucher")
    voucher_attachment_id = fields.Many2one('ir.attachment', string="Voucher Attachment")
    hotel_attachment_id = fields.Many2one('ir.attachment', string="Hotel Document Attachment")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    status = fields.Selection([('draft','Draft'),('submit','Send')],default="draft",string="Status")
    room_per_person_details = fields.Char(compute="_compute_room_per_person_details", string="First Room/ Second Room")

    date_of_arrival_time = fields.Char(string=" Arrival Time to Hotel on Check in Date ")
    payment_status = fields.Selection([('payment_by_exhibitor', 'Payment By Exhibitor'), ('payment_by_hive', 'Payment By OMG')],default="payment_by_hive")
    hotel_address = fields.Text(string="Hotel Address")
    payment_by_omg = fields.Float(string="Payment By OMG(Days)")
    payment_by_exhibitor = fields.Float(string="Payment By Exhibitor(Days)")

    file_name = fields.Char()




    def action_view_records(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.attendee_full_name,
            'view_mode': 'form',
            'res_model': self._name,
            'target': 'current',
            'res_id': self.id,
        }






    @api.depends('exhibitor_contract_id')
    def _compute_room_per_person_details(self):
        for rec in self:
            rec.room_per_person_details = ""

    @api.onchange('upload_voucher')
    def change_status_upload_voucher(self):
        if self.upload_voucher:
            self.status = 'submit'
        else:
            self.status = 'draft'
    def write(self, vals):
        print(vals)
        file_name ='Hotel Booking Voucher'
        if self.file_name:
            file_name = self.file_name
        if 'upload_voucher' in vals:
            voucher_attachment = self.env['ir.attachment'].sudo().create({
                'name':file_name,
                'datas': vals['upload_voucher'],
                'type': 'binary',
                'public': True
            })
            print(voucher_attachment.local_url)
            vals['voucher_attachment_id'] = voucher_attachment.id
        res = super(ExhibitorHotelRequest, self).write(vals)
        print('write',res)


        #
        return res




    @api.depends('checkin_date', 'checkout_date')
    def _compute_number_of_nights(self):
        for rec in self:
            no_of_nights = 0
            if rec.checkin_date and rec.checkout_date:
                date_diff = rec.checkout_date - rec.checkin_date
                no_of_nights = date_diff.days
            rec.no_of_nights = no_of_nights

    def download_hotel_uploaded_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.hotel_attachment_id.id,
            'target': 'self',
        }

    def approve_hotel_request(self):
        if not self.hotel_name or not self.no_of_rooms or not self.hotel_booking_ref or not self.upload_voucher:
            raise ValidationError(_('Please add the relevant details'))
        self.write({
            'booking_status': 'completed'
        })

    def reset_to_pending(self):
        self.write({
            'booking_status': 'pending'
        })

    def action_view_hotel_booking_sale_orders(self):
        self.ensure_one()
        action = {
            'name': _("Sale Orders"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }
        sale_order_ids = self.sale_order_id.ids
        if len(sale_order_ids) == 1:
            sale_order = sale_order_ids[0]
            action['res_id'] = sale_order
            action['view_mode'] = 'form'
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', sale_order_ids)]

        return action
    def unlink(self):
        is_portal = self.env.user.has_group('base.group_portal')
        if self.exhibitor_contract_id.maximum_hotel_booking_delete <= 0:
            self.exhibitor_contract_id.is_submited_hotel_request = False
        if is_portal:
            self.exhibitor_contract_id.maximum_hotel_booking_delete =   self.exhibitor_contract_id.maximum_hotel_booking_delete  - 1
        return super().unlink()
