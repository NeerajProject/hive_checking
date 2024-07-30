from odoo import models

import xlsxwriter
import base64
from datetime import datetime, date
from datetime import datetime, timedelta

import io
class PartnerXlsx(models.AbstractModel):
    _name = 'report.aegc_calender_customization.report_calendar_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        excel_data_sheet = {}
        date_of_entry = lines.date_of_entry
        operation_type_id = lines.operation_type_id
        appointment_all = self.env['calendar.event'].search([('start_date_real_date', '=', date_of_entry), (
        'appointment_type_id', 'in', operation_type_id.ids)])
        for rec in operation_type_id:
            slots = rec.generate_time_slots(date_of_entry, appointment_all)
            excel_data_sheet[rec.name] = slots

        print('excel_data_sheet',excel_data_sheet)

        for attendee_type in excel_data_sheet.keys():
            sheet = workbook.add_worksheet(attendee_type)

            sheet.set_default_row(20)
            row = 0
            col = 0
            sheet.set_column(0, 0, 10)
            sheet.set_column(1, 1, 35)
            sheet.set_column(2, 2, 35)
            sheet.set_column(3, 3, 35)
            sheet.set_column(4, 4, 35)
            sheet.set_column(5, 5, 35)
            heading_style = workbook.add_format({'font_size': '20px', 'align': 'center', 'bg_color': '#efefef'})
            sheet.merge_range(row, col, row + 1, col + 4, attendee_type, heading_style)
            row = row + 1
            row = row + 1
            headers_style = workbook.add_format({'font_size': '12px', 'align': 'center', 'bg_color': '#442e2e', 'font_color': '#f9f9f9'})
            attendee_color = workbook.add_format({'font_size': '10px', 'bg_color': '#fafce5'})
            sheet.merge_range(row, col, row, col + 4, date_of_entry.strftime("%A, %d %B, %Y"), headers_style)
            style_header = workbook.add_format({'border':True,'font_size': '14px', 'align': 'center', 'bg_color': '#FFE79F','text_wrap': True})
            row = row + 1
            sheet.write(row, col, "Time", style_header)
            sheet.set_column(row, col, 12)
            sheet.write(row, col + 1, "Player 1", style_header)
            sheet.set_column(row, col + 1, 30)
            sheet.write(row, col + 2, "Player 2", style_header)
            sheet.set_column(row, col + 2, 30)

            sheet.write(row, col + 3, "Player 3", style_header)
            sheet.set_column(row, col + 3, 30)

            sheet.write(row, col + 4, "Player 4", style_header)
            sheet.set_column(row, col + 4, 30)

            for record in excel_data_sheet[attendee_type]:
                row = row + 1
                col = 0

                sheet.write(row, col, record['time_in_text'])

                if record['is_event']:
                    attendee_color_event = workbook.add_format({'font_size': '10px', 'bg_color': record['color']})

                    col = col+1
                    sheet.write(row, col, record['name'], attendee_color_event)
                    col = col+1
                    sheet.write(row, col, record['name'], attendee_color_event)
                    col = col+1
                    sheet.write(row, col, record['name'], attendee_color_event)
                    col = col+1
                    sheet.write(row, col, record['name'], attendee_color_event)


                col = 0
                for partner in record['partner_ids']:
                    col = col + 1
                    if record['is_event']:
                        sheet.write(row, col, partner+" | "+record['name'],attendee_color_event)
                    else:
                        sheet.write(row, col, partner,attendee_color)




        #         for attendee in slot_list[record]['attendees']:
        #             col = col + 1
        #             print(attendee)
        #             sheet.write(row, col, attendee, attendee_color)
        #         col = 0
