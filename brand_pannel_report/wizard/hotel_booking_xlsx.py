from odoo import models, fields, api

from odoo.tools.image import image_data_uri

import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.tools import float_is_zero
from odoo.tools import date_utils
import io
import json
from io import BytesIO

import base64
from datetime import datetime

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter

def get_24hr_to_12hr(time_str):
    if time_str:
            time_obj = datetime.strptime(time_str, '%H:%M')
            time_12hour = time_obj.strftime('%I:%M %p')
            return time_12hour
    else:
        return False

class ReportHotelBookingXlsx(models.AbstractModel):
    _name = 'report.brand_pannel_report.report_hotel_booking_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, lines):
        hotel_booking_ids = self.env['exhibitor.hotel.request'].search([('event_id', '=', lines.event_id.id)])
        sheet = workbook.add_worksheet(lines.event_id.name)
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )
        cell_format = workbook.add_format({'bold': True, 'bg_color': 'orange'})

        sheet.merge_range(0, 0, 0, 15, str(lines.event_id.name)+" HOTEL REPORT ", merge_format)
        first_column = [

            'Attendee Name','AGENT REF','Brand','Company Name','Country','Email','Mobile','Booking Status','Check In Date','Check Out Date',
            'First Room / Second Room' ,'BOOK REF NO.','Hotel Name','No.of Rooms', 'Eligible No.of Nights', 'BOOKED NO.OF  NIGHTS',
            'PAYMENT BY OMG(DAYS)' ,
            'PAYMENT BY EXHIBITOR(DAYS)',
            'ARRIVAL TIME'

        ]
        print(len(first_column))
        row = 1
        col = 0
        sheet.set_column(0, 15, 40)
        for rec in first_column:
            sheet.write(1, col, rec, cell_format)
            col = col + 1
        row = row + 1
        col = 0
        for rec in hotel_booking_ids:
            col = 0
            sheet.write(row, col, rec.attendee_full_name)
            col = col + 1
            if  rec.exhibitor_contract_id.agent_id:
                sheet.write(row, col, rec.exhibitor_contract_id.agent_id.name)
            else:
                sheet.write(row, col, '')
                if rec.exhibitor_contract_id.sale_order_id:
                    if rec.exhibitor_contract_id.sale_order_id.opportunity_id:
                        if rec.exhibitor_contract_id.sale_order_id.opportunity_id.reference_id:
                            sheet.write(row, col,rec.exhibitor_contract_id.sale_order_id.opportunity_id.reference_id.name)



            col = col + 1
            if rec.exhibitor_contract_id.brand_id:
                sheet.write(row, col, rec.exhibitor_contract_id.brand_id.name)
            else:
                sheet.write(row, col, '')
            col = col + 1
            sheet.write(row, col, rec.exhibitor_contract_id.company_name)
            col = col + 1
            if rec.attendee_id.country_id:
                sheet.write(row, col, rec.attendee_id.country_id.name)
            else:
                sheet.write(row, col, rec.exhibitor_contract_id.company_name)
            col = col + 1
            sheet.write(row, col, rec.attendee_id.email)
            col = col + 1
            mobile = ''
            if rec.attendee_id.country_code:
                mobile=rec.attendee_id.country_code.code+"-"
            if rec.attendee_id.mobile:
                mobile = mobile+rec.attendee_id.mobile
            sheet.write(row, col, mobile)
            col = col + 1
            if  rec.booking_status:
                sheet.write(row, col, rec.booking_status.upper())
            else:
                sheet.write(row, col, '')
            col = col + 1
            sheet.write(row, col, str(rec.checkin_date))

            col = col + 1

            sheet.write(row, col, str(rec.checkout_date))

            col = col + 1

            sheet.write(row, col, rec.room_id)

            col = col + 1
            sheet.write(row, col, rec.hotel_booking_ref)

            col = col + 1
            sheet.write(row, col,rec.hotel_name)

            col = col + 1

            sheet.write(row, col, rec.no_of_rooms)

            col = col + 1


            sheet.write(row, col, rec.allowed_no_of_nights)

            col = col + 1

            sheet.write(row, col, rec.no_of_nights)

            col = col + 1

            sheet.write(row, col, rec.payment_by_omg)

            col = col + 1
            sheet.write(row, col, rec.payment_by_exhibitor)

            col = col + 1

            sheet.write(row, col, get_24hr_to_12hr(rec.date_of_arrival_time))

            col = col + 1
            row = row + 1
class ReportHotelBooking(models.TransientModel):
    _name = 'report.hotel.booking'
    event_id = fields.Many2one('event.event', string="Event")


    def action_export_report_hotel_booking(self):
        return self.env.ref('brand_pannel_report.report_hotel_booking_xlsx').report_action(self, data={})
