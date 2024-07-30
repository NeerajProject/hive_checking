# -*- coding: utf-8 -*-

import base64
import json
import logging
import requests
from datetime import datetime

from odoo import http
from odoo.exceptions import Warning
from odoo.http import request, Response
from odoo.osv.expression import OR, AND
import base64
_logger = logging.getLogger(__name__)


class ExhibitorDashboardController(http.Controller):

    @http.route('/submit/brand/branding_panel', type='http', auth='user', website=True, csrf=False)
    def submit_branding_panel(self, **kw):
        contract_id = request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['id']))])
        contract_id.branding_panel_status = 'confirm'
        return request.redirect("/exhibitor_dashboard/exhibitor_branding_panel?successfully_branding_submit=true")
    @http.route('/decline/floor/plan', type='http', auth='user', website=True, csrf=False)
    def declined_floor_plan_exhibitor_document_upload(self, **kw):
        floor_plan_documents_id = request.env['booth.design.line'].sudo().search([('id', '=', int(kw['id']))])
        print('remove_floor_plan_exhibitor_document_upload', floor_plan_documents_id)
        floor_plan_documents_id.status = 'decline'
        return request.redirect("/exhibitor_dashboard/exhibitor_floor_plan?success_branding_panel=true")
    @http.route('/cancel/floor/plan', type='http', auth='user', website=True, csrf=False)
    def remove_floor_plan_exhibitor_document_upload(self,**kw):
        floor_plan_documents_id = request.env['booth.design.line'].sudo().search([('id', '=', int(kw['id']))])
        print('remove_floor_plan_exhibitor_document_upload',floor_plan_documents_id)
        floor_plan_documents_id.status = 'cancel'
        return request.redirect("/exhibitor_dashboard/exhibitor_floor_plan?success_branding_panel=true")

    @http.route('/submit/floor_plan/document_submit', type='http', auth='user', website=True, csrf=False)
    def submit_floor_plan_exhibitor_document_upload(self,**kw):
        print("submit_floor_plan_exhibitor_document_upload",kw)
        stand_id = False
        document_type_id = False
        exh_comments = False
        if not(kw['stand_id'] == ''):
            stand_id = int(kw['stand_id'])
        if not(kw['document_type_id'] == ''):
            document_type_id = int(kw['document_type_id'])
        if 'exh_comments' in kw.keys():
            exh_comments = kw['exh_comments']
        print('stand_id',stand_id,'document_type_id',document_type_id,'exh_comments',exh_comments)

        booth_design_line_id=request.env['booth.design.line'].sudo().create({
            'stand_id':stand_id,
            'booth_design_id':document_type_id,
            'description'  : exh_comments,
            'exhibitor_contract_id': int(kw['contract_id']),
            'status': 'submitted',
            'by_iff_exihibitor':'exhibitor'

        })
        print(">>>>>>>>>>>>>>>>>>>>>>ssss",booth_design_line_id.read())

        if 'document_upload' in kw.keys():
            document_file = kw['document_upload']
            if document_file.filename:
                if document_file.filename:
                    document_attachment = request.env['ir.attachment'].sudo().create({
                        'name': document_file.filename,
                        'datas': base64.encodebytes(document_file.read()),
                        'type': 'binary',
                        'public': True
                    })
                    booth_design_line_id.attachement_ids = [document_attachment.id]

        if booth_design_line_id.booth_design_id:
            if booth_design_line_id.attachement_ids:
                request.env['mail.activity'].sudo().create(
                    {'res_name': "You have a message",
                     'company_name': booth_design_line_id.exhibitor_contract_id.company_name,
                     'section': 'Stand Design Info',
                     'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                     'res_name': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " --  " + str(
                         booth_design_line_id.booth_design_id.name) + "/" + str(
                         booth_design_line_id.attachement_ids.name),
                     'summary': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " --  " + str(
                         booth_design_line_id.booth_design_id.name) + "/" + str(
                         booth_design_line_id.attachement_ids.name),
                     'user_id': request.env.user.id,
                     'res_model_id': request.env.ref('brand_pannel_hive.model_booth_design_line').id,
                     'res_id': booth_design_line_id.id
                     })
            else:
                request.env['mail.activity'].sudo().create(
                    {'res_name': "You have a message",
                     'company_name': booth_design_line_id.exhibitor_contract_id.company_name,
                     'section': 'Stand Design Info',
                     'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                     'res_name': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " --  " + str(
                         booth_design_line_id.booth_design_id.name),
                     'summary': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " -- " + str(
                         booth_design_line_id.booth_design_id.name),
                     'user_id': request.env.user.id,
                     'res_model_id': request.env.ref('brand_pannel_hive.model_booth_design_line').id,
                     'res_id': booth_design_line_id.id
                     })
        else:
            request.env['mail.activity'].sudo().create(
                {'res_name': "You have a message",
                 'company_name': booth_design_line_id.exhibitor_contract_id.company_name,
                 'section': 'Stand Design Info',
                 'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                 'res_name': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " --  ",
                 'summary': 'You have a Stand Design Info from ' + request.env.user.partner_id.name + " -- ",
                 'user_id': request.env.user.id,
                 'res_model_id': request.env.ref('brand_pannel_hive.model_booth_design_line').id,
                 'res_id': booth_design_line_id.id
                 })

        booth_design_line_id.sent_stand_info_to_hive()

        return request.redirect("/exhibitor_dashboard/exhibitor_floor_plan?success_branding_panel=true")


    @http.route('/upload/exhibitor/floor/plan', type='http', auth='user', website=True, csrf=False)
    def submit_exhibitor_document_upload(self,**kw):
        print(kw)
        if 'id' in kw.keys():
            floor_plan =  request.env['booth.design.line'].sudo().search([('id','=',int(kw['id']))])
            document_file = kw['exhibitor_file_upload']
            if document_file.filename:
                if document_file.filename:
                    document_attachment = request.env['ir.attachment'].sudo().create({
                        'name': document_file.filename,
                        'datas': base64.encodebytes(document_file.read()),
                        'type': 'binary',
                        'public': True
                    })
                    print('upload plan kw',kw)
                    floor_plan.exhibitor_upload= document_attachment.id
                    if 'by_iff_exihibitor' in kw.keys():

                        floor_plan.by_iff_exihibitor = kw['by_iff_exihibitor']
                    floor_plan.message_post(body='Exhibitor uploaded floor Plan', attachments=document_attachment)


        return  request.redirect("/exhibitor_dashboard/exhibitor_floor_plan")

    @http.route('/submit/branding_panel/category', type='http', auth='user', website=True, csrf=False)
    def add_product_category(self,**kw):
        accessories_branding =[]
        furniture_branding =[]
        contractor =  request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['contract_id']))])
        print(kw)
        if 'is_other_accessory' in kw.keys():
            contractor.is_other_accessory = kw['is_other_accessory']
        if 'is_other_furniture' in kw.keys():
            contractor.is_other_furniture = kw['is_other_furniture']


        for rec in kw.keys():
            if 'accessories.branding.type(' in rec:
                accessories_branding.append(int(kw[rec]))
            if 'furniture.branding.type(' in rec:
                furniture_branding.append(int(kw[rec]))

        contractor.sudo().write({
            'category_accessories': accessories_branding,
            'category_furniture': furniture_branding})

        activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': contractor.company_name,
            'section': 'Branding Panel Categories Submitted',
            'res_name': contractor.name + "    Branding Panel Categories Submitted",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contractor.partner_id.name + "  Branding Panel Categories Submitted",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contractor.id
        })
        return  request.redirect("/exhibitor_dashboard/exhibitor_branding_panel?category_submit=true")

    @http.route('/submit/branding_panel/category/remove', type='http', auth='user', website=True, csrf=False)
    def clear_all_category(self,**kw):
        print('clear_all_category',kw)
        contractor =  request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['id']))])
        contractor.is_other_accessory = False
        contractor.is_other_furniture = False
        contractor.category_accessories = False
        contractor.category_furniture = False

        activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': contractor.company_name,
            'section': 'Branding Panel Submitted Logo',
            'res_name': contractor.name + "    Branding Panel Categories Cleared",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contractor.partner_id.name + "  Branding Panel Categories Cleared",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contractor.id
        })

        return  request.redirect("/exhibitor_dashboard/exhibitor_branding_panel")


        # contractor

    @http.route('/submit/branding_panel/logo', type='http', auth='user', website=True, csrf=False)
    def submit_branding_info_logo(self,**kw):
        print(kw)

        contractor =  request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['contract_id']))])
        if 'branding_company_name' in kw.keys():
            contractor.branding_panel_company_name = kw['branding_company_name'].upper()
        if 'exh_document' in kw.keys():
            if str(kw.get('exh_document')) == "<FileStorage: '' ('application/octet-stream')>":
                pass
            else:
                contractor.company_logo = base64.b64encode(kw.get('exh_document').read())
        contractor.branding_panel_status = 'confirm'

        activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': contractor.company_name,
            'section': 'Branding Panel Submitted Logo',
            'res_name': contractor.name + "  Branding Panel Logo",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contractor.partner_id.name + "  Branding Panel Logo Submitted",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref(                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contractor.id
        })
        return  request.redirect("/exhibitor_dashboard/exhibitor_branding_panel?branding_successfully_submit=true")


    @http.route('/accepted/floor/plan', type='http', auth='user', website=True, csrf=False)
    def accepted_stand_line_plan(self,**kw):
        record = request.env['booth.design.line'].sudo().search([('id','=',int(kw['id']))])
        record.status = 'accepted'
        print(record.read())

        activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': record.exhibitor_contract_id.company_name,
            'section': 'Floor Planning',
            'res_name':  record.booth_design_id.name or '' + "  Accepted 'Floor Planning",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': record.exhibitor_contract_id.partner_id.name + " Accepted Branding Info",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref(
                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id':record.exhibitor_contract_id.id
        })

        return  request.redirect("/exhibitor_dashboard/exhibitor_floor_plan?submited_request=True")

    @http.route('/exhibitor_dashboard/exhibitor_floor_plan/floor', type='http', auth='user', website=True, csrf=False)
    def suggestion_panel(self,**kw):
        values={}
        print(kw)
        user = request.env.user

        if user.user_category == 'exhibitor':
           floor_plan_documents_id = request.env['booth.design.line'].sudo().search([('id','=',int(kw['id']))])
           values['floor_plan_documents_id'] = floor_plan_documents_id
           values['id'] = int(kw['id'])


           return request.render("brand_pannel_hive.portal_exhibitor_floor_suggestion_plan", values)
        else:
            return request.redirect("/exhibitor_dashboard/exhibitor_floor_plan")

    @http.route('/edit/stands/portal', type='http', auth='user', website=True, csrf=False)
    def update_stand_details(self, **kw):
        print('update_stand_details',kw)
        stands_list = request.env['branding.update.line'].sudo().search([('id','=',int(kw['custom_stand_id']))])
        if stands_list._check_already_update_exist(int(kw['stand_id'])):
            return request.redirect('/exhibitor_dashboard/exhibitor_branding_panel?already_exist_stand=true')

        else:
            stands_list.stand_id =int(kw['stand_id'])
            return  request.redirect("/exhibitor_dashboard/exhibitor_branding_panel?update=True")

    @http.route('/exhibitor_dashboard/exhibitor_branding_panel', type='http', auth='user', website=True, csrf=False)
    def portal_branding_panel(self, **kw):

        user = request.env.user
        values ={}
        values['preview'] = False
        values['edit'] = False
        values['stand_id'] = False
        values['update'] = False
        values['already_exist_stand'] = False
        values['category_submit'] = False
        values['successfully_submit'] =False
        values['branding_successfully_submit'] = False
        if 'branding_successfully_submit' in kw.keys():
            values['branding_successfully_submit'] = True

        if 'successfully_submit' in kw.keys():
            values['successfully_submit'] = True
        if 'category_submit' in kw.keys():
            values['category_submit'] = True

        if 'already_exist_stand' in kw.keys():
            values['already_exist_stand'] = True

        if 'update' in kw.keys():
            values['update'] = True




        if user.user_category == 'exhibitor':


            if 'preview' in kw.keys():
                values['preview'] = True
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)

            ], limit=1)
            accessories = request.env['accessories.branding.type'].search([],order='sequence ASC')
            furniture = request.env['furniture.branding.type'].search([],order='sequence ASC')
            values['accessories'] = accessories
            values['furniture'] = furniture
            values['contract'] = contract

            values['accessories_checked'] = contract.category_accessories.mapped('id')
            values['furniture_checked'] = contract.category_furniture.mapped('id')
            print('kw',kw)
            stands_details = False
            stands_list = False
            hall_list =[]
            default_stand_id =False
            if 'stand_id' in kw.keys():
                stands_details = contract.stand_ids.filtered(lambda record: record.id == int(kw['stand_id']))
                values['stands_details'] = stands_details
                values['default_stand_id'] = stands_details.stand_id.id
                values['default_hall_id'] = stands_details.hall_id.id
                values['stands_for_edit'] =  contract.stand_ids
            values['is_exhibitor'] = request.env.user.user_category

            if 'stand_id' in kw.keys() and 'edit' in kw.keys():
                values['edit'] = kw['edit']
                values['stand_id'] = int(kw['stand_id'])
                values['default_stand_id'] = contract.brand_panel_ids.filtered(lambda record: record.id == int(kw['stand_id']))
            print("yyy",values)
            return request.render("brand_pannel_hive.portal_exhibitor_branding_panel", values)


    @http.route('/exhibitor_dashboard/exhibitor_floor_plan', type='http', auth='user', website=True, csrf=False)
    def portal_floor_plan(self, **kw):
        user = request.env.user
        values = {}
        values['documents_type_ids'] = request.env['booth.design.type'].sudo().search([])
        if user.user_category == 'exhibitor':
            print("portal_branding_panel")
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            values['contract'] = contract
            values['submited_request'] = False
        if 'submited_request' in kw.keys():
            values['submited_request'] =kw['submited_request']

        values['is_exhibitor'] = request.env.user.user_category
        return request.render("brand_pannel_hive.portal_exhibitor_floor_plan", values)

    @http.route('/submit/branding_panel', type='http', auth='user', website=True, csrf=False)
    def portal_submit(self, **kw):
        print(kw)
        furniture_branding  = []
        accessories_branding = []
        user = request.env.user
        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            contract.is_submited_branding_panel = True
            contract.category_accessories = False
            contract.category_furniture = False
            contract.category_accessories = []
            contract.category_furniture = []
            for rec in kw.keys():
                if 'accessories.branding.type(' in rec:
                    accessories_branding.append(int(kw[rec]))
                if 'furniture.branding.type(' in rec:
                    furniture_branding.append(int(kw[rec]))

            contract.sudo().write({
                'category_accessories' : accessories_branding,
                'category_furniture' :furniture_branding})

            if 'branding_company_name' in kw.keys():
                contract.branding_panel_company_name =kw['branding_company_name'].upper()
            if 'exh_document' in kw.keys():
                if str(kw.get('exh_document'))=="<FileStorage: '' ('application/octet-stream')>":
                    pass
                else:
                    contract.company_logo = base64.b64encode(kw.get('exh_document').read())

            activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': contract.company_name,
            'section': 'Branding Info',
            'res_name': contract.name + "  Submitted Branding Info",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contract.partner_id.name + " Submitted Branding Info",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref(
                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contract.id
            })


        return request.redirect("/exhibitor_dashboard/exhibitor_branding_panel?preview=true")


    @http.route('/exhibitor_dashboard/exhibitor_floor_plan/accept', type='http', auth='user', website=True, csrf=False)
    def action_accept_plan(self, **kw):
        user = request.env.user
        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            contract.is_accepted_floorplan = True


            activity_id = request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': contract.company_name,
            'section': 'Floor Planning',
            'res_name': contract.name + "  Accepted 'Floor Planning",
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contract.partner_id.name + " Submitted Branding Info",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref(
                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contract.id
            })

            return request.redirect('/exhibitor_dashboard/exhibitor_floor_plan')
    @http.route('/exhibitor_dashboard/exhibitor_floor_plan/decline', type='http', auth='user', website=True, csrf=False)
    def action_declined_plan(self, **kw):
        user = request.env.user
        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            contract.is_accepted_floorplan = False
            return request.redirect('/exhibitor_dashboard/exhibitor_floor_plan')

    @http.route('/submit/stands/portal', type='http', auth='user', website=True, csrf=False)
    def submit_stands_portal(self, **kw):

        contract = request.env['exhibitor.contract'].sudo().search([
            ('id', '=', int(kw['contract_id']))
        ], limit=1)
        if contract.check_count_is_okay():
                if request.env['branding.update.line'].sudo()._check_already_exist(int(kw['stand_id']), contract.event_id.id):
                    return request.redirect('/exhibitor_dashboard/exhibitor_branding_panel?already_exist_stand=true')

                else:
                    request.env['branding.update.line'].sudo().create({
                        'exhibitor_contract_id' : contract.id,
                        'stand_id':int(kw['stand_id'])
                    })
        return request.redirect('/exhibitor_dashboard/exhibitor_branding_panel')