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

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter


class ReportBrandingPanelXlsx(models.AbstractModel):
    _name = 'report.brand_pannel_report.branding_panel_xlsx_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        exhibitor_contractor_ids =self.env['exhibitor.contract'].sudo().search([('event_id','=',lines.event_id.id)])
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

        sheet.merge_range(0,0,0,6, "BRANDING PANEL REPORT", merge_format)
        first_column=['Registered Company Name','Company Name required on Panel',	'AGENT REFERENCE',	'HALL NO.'	, 'Stand Number',	 'Panel Width in MTR' 	, 'Panel Height in MTR']
        row=1
        col = 0
        sheet.set_column(0,6,40)
        for rec in first_column:
            sheet.write(1, col, rec,cell_format)
            col = col + 1
        row = row+1
        for rec in exhibitor_contractor_ids:
            col = 0
            sheet.write(row, col, rec.company_name)
            col=col+1
            sheet.write(row, col, rec.branding_panel_company_name)
            col = col + 1
            if rec.reference_id:
                sheet.write(row, col, rec.reference_id.name)
            else:
                sheet.write(row, col, '')

            col = col + 1

            sheet.write(row, col, rec.hall_number)
            col = col + 1

            sheet.write(row, col, ', '.join(rec.sale_order_id.stand_ids.mapped('stand_number')))
            col = col + 1
            sheet.write(row, col, rec.branding_panel_width)
            col = col + 1
            sheet.write(row, col, rec.branding_panel_height)
            col = col + 1
            row = row+1


class ReportBrandingPanel(models.TransientModel):
   _name = 'report.branding.panel'
   _rec_name = 'event_id'
   event_id = fields.Many2one('event.event',string="Event")

   def action_export_branding_panel_report(self):
       return self.env.ref('brand_pannel_report.branding_panel_xlsx_report_xlsx').report_action(self, data={})

# Stand design Details

class ReportStandDesignXlsx(models.AbstractModel):
    _name = 'report.brand_pannel_report.stand_design_xlsx_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, lines):
        booth_design_line =self.env['booth.design.line'].sudo().search([('event_id','=',lines.event_id.id)])
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

        sheet.merge_range(0,0,0,11, "STAND DESIGN REPORT", merge_format)
        first_column=['SEQUENCE','DATE','COMPANY NAME','BRAND NAME','REFERENCE','HALL NO.','STAND NO.','TYPE', 'BY OMG OR EXHIBITOR','COMMENTS','FILE NAME','STATUS' ]
        row=1
        col = 0
        sheet.set_column(0,12,30)
        for rec in first_column:
            sheet.write(1, col, rec,cell_format)
            col = col + 1
        row = row+1
        sequence = 0
        for rec in booth_design_line:
            col = 0
            sequence = sequence+1
            sheet.write(row, col, sequence)
            col = col + 1
            sheet.write(row, col, str(rec.date_of_upload))
            print(rec.date_of_upload)
            col = col + 1
            sheet.write(row, col, rec.exhibitor_contract_id.company_name)
            col = col + 1
            if rec.exhibitor_contract_id.brand_id:
                sheet.write(row, col, rec.exhibitor_contract_id.brand_id.name)
            else:
                sheet.write(row, col, '')
            col = col + 1
            if rec.exhibitor_contract_id.reference_id:
                sheet.write(row, col, rec.exhibitor_contract_id.reference_id.name)
            else:
                sheet.write(row, col, '')
                if rec.exhibitor_contract_id.sale_order_id:
                    if rec.exhibitor_contract_id.sale_order_id.opportunity_id:
                        if rec.exhibitor_contract_id.sale_order_id.opportunity_id.reference_id:
                            sheet.write(row, col,rec.exhibitor_contract_id.sale_order_id.opportunity_id.reference_id.name)

            col = col+1

            sheet.write(row, col, rec.exhibitor_contract_id.hall_number)
            col = col + 1

            sheet.write(row, col, ', '.join(rec.exhibitor_contract_id.sale_order_id.stand_ids.mapped('stand_number')))
            col = col + 1
            if rec.booth_design_id:
                sheet.write(row, col, rec.booth_design_id.name)
            else:
                sheet.write(row, col, '')
            col = col + 1
            if  rec.by_iff_exihibitor:
                sheet.write(row, col, rec.by_iff_exihibitor.upper())
            else:
                sheet.write(row, col, '')

            col = col + 1
            sheet.write(row, col, rec.description)
            col = col+1
            filenames =''
            for file in rec.attachement_ids:
                filenames=filenames + file.name+"\n"


            sheet.write(row, col, filenames)
            col = col + 1
            sheet.write(row,col,rec.status.upper())

            row = row+1



class ReportStandDesign(models.TransientModel):
   _name = 'report.stand.design'
   event_id = fields.Many2one('event.event',string="Event")

   def action_export_stand_design_report(self):
       return self.env.ref('brand_pannel_report.stand_design_xlsx_report_xlsx').report_action(self, data={})





# category report

class ReportBrandCategoryXlsx(models.AbstractModel):
    _name = 'report.brand_pannel_report.report_brand_category_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, lines):
        exhibitor_contractor_ids = self.env['exhibitor.contract'].sudo().search([('event_id', '=', lines.event_id.id)])
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

        sheet.merge_range(0, 0, 0, 10, "CATEGORIES REPORT", merge_format)
        first_column = ['BRAND','COMPANY NAME','AGENT REFERENCE','COUNTRY','CONTACT NO.','EMAIL ID',
                        'WEBSITE',
                        'HALL NO.',
                        'STAND NO.','MAIN CATEGORY','SUB CATEGORY'
                        ]
        print(len(first_column))
        row =1
        col = 0
        sheet.set_column(0 ,10 ,40)
        for rec in first_column:
            sheet.write(1, col, rec ,cell_format)
            col = col + 1
        row = row +1
        for rec in exhibitor_contractor_ids:
            col = 0
            if rec.brand_id:
                sheet.write(row, col, rec.brand_id.name)
            else:
                sheet.write(row, col, "")
            col = col + 1
            sheet.write(row, col, rec.company_name)

            col = col + 1
            if rec.reference_id:
                sheet.write(row, col, rec.reference_id.name)
            else:
                sheet.write(row, col, '')
                if rec.sale_order_id:
                    if rec.sale_order_id.reference_id:
                        if rec.sale_order_id.opportunity_id.reference_id:
                            sheet.write(row, col,
                                        rec.sale_order_id.opportunity_id.reference_id.name)

            col = col + 1
            sheet.write(row, col, rec.country_name)
            col = col + 1
            sheet.write(row, col, str(rec.mobile)+"\n"+str(rec.landline))
            col = col + 1
            sheet.write(row, col, rec.email)
            col = col + 1
            sheet.write(row, col, rec.partner_id.website)
            col = col + 1
            sheet.write(row, col, rec.hall_number)
            col = col + 1
            sheet.write(row, col, ', '.join(rec.sale_order_id.stand_ids.mapped('stand_number')))
            col = col + 1
            sheet.write(row, col, 'FURNITURE')
            col = col + 1
            for furniture in rec.category_furniture:
                if furniture.is_others:
                    sheet.write(row, col, str(rec.is_other_furniture)+" - "+str(furniture.name)+"")
                    row = row+1
                else:

                    sheet.write(row, col, furniture.name)
                    row = row+1
            col = col -1
            sheet.write(row, col, 'ACCESSORIES')
            col = col + 1
            for accessories in rec.category_accessories:

                if accessories.is_others:
                    sheet.write(row, col, str(rec.is_other_accessory) + " -  " + str(accessories.name) + "")
                    row = row + 1
                else:
                    sheet.write(row, col, accessories.name)
                    row = row + 1

            row=row+1
class ReportBrandCategory(models.TransientModel):
    _name = 'report.brand.category'
    event_id = fields.Many2one('event.event', string="Event")


    def action_export_report_brand_category(self):
        return self.env.ref('brand_pannel_report.report_brand_category_xlsx').report_action(self, data={})
