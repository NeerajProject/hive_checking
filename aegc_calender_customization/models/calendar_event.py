from odoo import fields, models, _, api
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date, datetime, time
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class MembershipDetails(models.Model):
    _name = 'membership.type.info'

    calendar_event_id = fields.Many2one('calendar.event', store=True)
    name = fields.Char(string="name")
    partner_id = fields.Many2one('res.partner', string='Attendees', store=True)
    membership_id = fields.Many2one('product.product', string="Membership", readonly=True, store=True)
    product_id = fields.Many2one('product.template', readonly=False,string="Product",store=True)
    ninth_hole_only = fields.Boolean(string="9th hole only")
    membership_type_id = fields.Many2one('membership.type',
                                         string="Membership Type", store=True)
    start_date = fields.Date(string="Start Date", store=True)
    expiry_date = fields.Date(string="Expiry Date", store=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_golf = fields.Boolean()


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # def action_draft(self):
    #     self.state='draft'

    product_ids = fields.Many2many('product.template', domain=[('is_golf', '=', True)])
    is_single_invoice = fields.Boolean()
    state = fields.Selection([('draft', 'Draft'), ('invoice', 'Invoiced')], default="draft")
    start_date_real_date = fields.Date(compute="compute_search_date",store=True)
    real_start_date_in_db = fields.Datetime()
    eighteen_points = fields.Boolean(string="9th Hole Only")
    eighteen_points_appointment_id = fields.Many2one('calendar.event')
    is_18_point_created = fields.Boolean()
    next_available_slot = fields.Datetime()
    show_available_slots = fields.Datetime(compute="_compute_next_available_slot")
    computed_available_slots = fields.Datetime(compute="_compute_suggested_available_slot")
    is_visible_to_18_holes = fields.Boolean(related='appointment_type_id.is_eighteen_points')
    show_available_slots_stored = fields.Datetime()
    computed_available_slots_stored = fields.Datetime()
    account_move_ids = fields.One2many('account.move','calender_event_id')
    is_reloaded= fields.Boolean(default=True)
    invoice_ids = fields.Many2many('account.move')

    payment_status = fields.Selection([('not_invoiced', 'Not invoiced'), ('not_paid', 'Not Paid'), ('paid', 'Paid')],
                                      compute="compute_set_payment_status")

    slots_to_book_available = fields.Datetime()




    membership_types_ids = fields.One2many('membership.type.info',
                                           'calendar_event_id',
                                           string='Membership Type',
                                           store=True)




    def unlink(self):
        total = 0
        for rec in   self.account_move_ids.filtered(lambda o: o.state == 'posted' and o.payment_state != 'not_paid'):
            total = total + rec.amount_total_in_currency_signed
        related_eighteen_points = self.env['calendar.event'].search([('eighteen_points_appointment_id','in',self.ids)])

        if related_eighteen_points:
           related_eighteen_points.unlink()

        if total == 0:
            return super(CalendarEvent, self).unlink()
        else:
            raise ValidationError("Please refund the Amount before Deletion")

    @api.onchange('partner_ids')
    def _get_membership_details(self):
        # """ Update the tree view and add new membership types when attendees are added """
        default_membership_type = self.env['membership.type'].sudo().search(
            [('name', '=', 'Guest'), ('club.name', '=', 'Golf Club')], limit=1)
        default_membership_type_id = default_membership_type.id if default_membership_type else False

        for rec in self:
            li = []
            self.membership_types_ids = [(5, 0, 0)]

            for p in rec.partner_ids:
                if p.member_lines:
                    for lines in p.member_lines.filtered(
                                lambda l: l.club_id.name == 'Golf Club' and l.expiry_date >= date.today()):
                        li.append((0, 0, {
                            'partner_id': lines.partner.id,
                            'membership_id': lines.membership_id.id,
                            'membership_type_id': lines.membership_type_id.id,
                            'start_date': lines.date,
                            'expiry_date': lines.expiry_date,
                        }))
                else:
                    li.append((0, 0, {
                        'partner_id': p.id,
                        'membership_id': '',
                        'membership_type_id': default_membership_type_id,
                        'start_date': False,
                        'expiry_date': False,
                    }))
            rec.sudo().membership_types_ids = li

    @api.depends('start','start_date_real_date')
    def compute_search_date(self):
        print("called")
        for rec in self:
            rec.start_date_real_date = rec.start
            print('compute_search_date',rec.start_date_real_date)

    def get_day_result_slots(self, apointment_date, operation_type_id):
        slots = operation_type_id._get_appointment_slots(self.env.user.tz)
        list_of_slots = []
        for rec in slots:
            for weeks in rec['weeks']:
                for days in weeks:
                    if days['day'].day == apointment_date.day and days['day'].month == apointment_date.month and days[
                        'day'].year == apointment_date.year:
                        list_of_slots = days
                        return {'slots': list_of_slots['slots'],
                                'appointment_type': operation_type_id.name, 'appointment_type_id': operation_type_id.id,
                                }

    def get_free_slots_in_of_eighteen_holes(self, calendar_event_id):
        calendar_event_id = self.env['calendar.event'].search([('id', '=', calendar_event_id)])
        apointment_date = calendar_event_id.start
        operation_type_id = calendar_event_id.appointment_type_id.eighteen_point_appointment_type
        list = self.get_day_result_slots(apointment_date, operation_type_id)
        available_list_of_slots = []

        apointment_date = apointment_date + timedelta(hours=4) + timedelta(
            minutes=calendar_event_id.appointment_type_id.span_of_eighteen_points)
        for rec in list['slots']:
            datetime_object = datetime.strptime(rec['datetime'], "%Y-%m-%d %H:%M:%S")
            if datetime_object >= apointment_date:
                print(datetime_object, " > ", apointment_date)
                available_list_of_slots.append(rec)
        list['slots'] = available_list_of_slots
        print('available_list_of_slots', available_list_of_slots)
        return list

    def action_change_date(self):
        start = self.show_available_slots
        end = self.show_available_slots + timedelta(
            hours=float(self.appointment_type_id.eighteen_point_appointment_type.appointment_duration))
        self.start = start
        self.stop = end
        self.name = self.appointment_type_id.name + '| Appointment | ' + str(self.start + timedelta(hours=4))

    def get_free_slots_in_of_available(self, calendar_event_id):
        calendar_event_id = self.env['calendar.event'].search([('id', '=', calendar_event_id)])
        apointment_date = calendar_event_id.start
        operation_type_id = calendar_event_id.appointment_type_id
        list = self.get_day_result_slots(apointment_date, operation_type_id)
        available_list_of_slots = []

        apointment_date = apointment_date + timedelta(hours=4)
        for rec in list['slots']:
            datetime_object = datetime.strptime(rec['datetime'], "%Y-%m-%d %H:%M:%S")
            available_list_of_slots.append(rec)
        list['slots'] = available_list_of_slots
        print('available_list_of_slots', available_list_of_slots)
        return list
    @api.depends('account_move_ids')
    def compute_set_payment_status(self):
        for record in self:

            record.payment_status = 'not_invoiced'
            for rec in record.account_move_ids:
                if rec.move_type=='out_refund':
                        record.payment_status = 'not_paid'
                        break
                else:
                    if rec.payment_state in ['in_payment', 'paid']:
                        record.payment_status = 'paid'
                        pass
                    else:
                        record.payment_status = 'not_paid'
                        break
            for rec in record.invoice_ids:
                if rec.move_type == 'out_refund':
                    record.payment_status = 'not_paid'
                    break
                else:
                    if rec.payment_state in ['in_payment', 'paid']:
                        record.payment_status = 'paid'
                        pass
                    else:
                        record.payment_status = 'not_paid'
                        break

    def _compute_suggested_available_slot(self):
        for rec in self:
            if rec.is_18_point_created:
                rec.computed_available_slots = rec.computed_available_slots_stored
            else:
                if rec.start:
                    rec.computed_available_slots = rec.start + timedelta(
                        minutes=rec.appointment_type_id.span_of_eighteen_points)

    def action_create_eighteen_holes(self):
        # for rec in self.membership_types_ids:
        #     print("yes i am tony",rec.read())
        membership_types_ids = self.membership_types_ids.filtered(lambda l: l.ninth_hole_only == False)

        if  membership_types_ids:
            if self.show_available_slots:
                start = self.show_available_slots
                end = self.show_available_slots + timedelta(
                    hours=float(self.appointment_type_id.eighteen_point_appointment_type.appointment_duration))
                event_id = self.env['calendar.event'].create({
                    'name': self.appointment_type_id.eighteen_point_appointment_type.name + '| Appointment ',
                    'attendee_ids': self.attendee_ids,
                    'appointment_type_id': self.appointment_type_id.eighteen_point_appointment_type.id,
                    'eighteen_points_appointment_id': self.id,
                    'duration': self.appointment_type_id.eighteen_point_appointment_type.appointment_duration,
                    'start': start,
                    'stop': end,
                    'start_date': start,
                    'stop_date': end,
                    'real_start_date_in_db': self.next_available_slot,
                    'start_date_real_date': self.next_available_slot,
                    'partner_ids': membership_types_ids.mapped('partner_id').ids
                 })

                for details in self.membership_types_ids:
                    lines = details.copy()
                    lines.calendar_event_id = event_id.id

                self.show_available_slots_stored = self.show_available_slots
                self.computed_available_slots_stored = self.computed_available_slots
                self.eighteen_points_appointment_id = event_id
                self.is_18_point_created = True
                event_id.name =event_id.name
            else:
                    raise ValidationError("Please Choose Available Slots")

        else:
            raise ValidationError("Please Choose Available Slots")

    def _compute_next_available_slot(self):
        for rec in self:
            if rec.is_18_point_created:
                rec.show_available_slots = rec.show_available_slots_stored
            else:
                if rec.next_available_slot:

                    rec.show_available_slots = rec.next_available_slot - timedelta(hours=4)
                else:
                    rec.show_available_slots = False

    def set_free_slots_in_of_eighteen_holes_date(self, appointment_id, next_available_slots):
        appointment_id = self.env['calendar.event'].search([('id', '=', appointment_id)])
        appointment_id.next_available_slot = next_available_slots
        return []

    def action_view_18_points(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "domain": ['|',('eighteen_points_appointment_id', '=', self.id),('id','=',self.eighteen_points_appointment_id.id)],
            "name": _("Related Appointment"),
            'view_mode': 'tree,form',
            'target': 'current'
        }
        return result

    def action_view_invoice(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": ['|',('calender_event_id', '=', self.id),('id','in',self.invoice_ids.ids)],
            "name": _("Customer Invoices"),
            'view_mode': 'tree,form',
            'target': 'current'
        }
        return result

    def action_create_invoice(self):
        # if self.product_ids:
        #     pass
        # else:
        #     raise ValidationError("Please Fill The Products")

        # if self.is_reloaded:
        #     self.is_reloaded = False
        #     return {
        #         'type': 'ir.actions.client',
        #         'tag': 'reload',
        #     }
        #
        if self.partner_ids:
            pass
        else:
            raise ValidationError("Please Fill Attendee")


        analytic_account=self.env['account.analytic.account'].sudo().search([('name','=','GOLF')],limit=1)
        club=self.env['res.club'].sudo().search([('name','=','Golf Club')],limit=1)

        if self.is_single_invoice:
            qty = len(self.partner_ids)
            partner_id = False
            for rec in self.membership_types_ids:
                partner_id = rec.partner_id.id
                product=rec.product_id.product_variant_id
                break

            account_id = self.env['account.move'].create({
                'name':'',
                'journal_id': 1,
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'analytic_account_id':analytic_account.id,
                'club_id':club.id,
                'calender_event_id': self.id
            })
            account_id._onchange_journal_id()

            # for product in self.product_ids:
            self.env['account.move.line'].create({

                'product_id': product.id,
                'quantity': qty,
                'price_unit': product.lst_price,
                'move_id': account_id.id
            })

            self.account_move_ids = [account_id.id]
            self.invoice_ids= [account_id.id]
            self.eighteen_points_appointment_id.invoice_ids= [account_id.id]
        else:
            account_ids = []
            # for rec in self.partner_ids:
            for rec in self.membership_types_ids:
                print("product",rec.product_id.product_variant_id.id)
                account_id = self.env['account.move'].create({
                    'name':'',
                    'journal_id':1,
                    'move_type': 'out_invoice',
                    'partner_id': rec.partner_id.id,
                    'calender_event_id': self.id,
                    'analytic_account_id': analytic_account.id,
                    'club_id': club.id,

                })
                account_id._onchange_journal_id()
                # print(e)
                # for product in self.product_ids:
                self.env['account.move.line'].create({
                    'product_id': rec.sudo().product_id.product_variant_id.id,
                    'quantity': 1,
                    'price_unit': rec.sudo().product_id.product_variant_id.lst_price,
                    'move_id': account_id.id
                })
                account_ids.append(account_id.id)
            self.account_move_ids = account_ids
            self.invoice_ids = account_ids
            self.eighteen_points_appointment_id.invoice_ids = account_ids
        self.eighteen_points_appointment_id.state = 'invoice'
        self.state = 'invoice'



class AccountMove(models.Model):
    _inherit = 'account.move'
    calender_event_id = fields.Many2one('calendar.event')



