# -*- coding: utf-8 -*-

import json
import logging
import requests
import base64

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import Warning
from datetime import datetime
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class ExhibitorRegistrationControllerPortal(http.Controller):

    @http.route('/submit/visitors/badge', type='http', auth='none', csrf=False)
    def badge_generation_visitors_badge_on_site(self,**kwarg):
            print(kwarg)
            event_id = request.env['event.event'].sudo().search([('id','=',int(kwarg['event_id']))])
            print("events",event_id.visitors_urls)
            if event_id.is_onsite:
                attendee = request.env['event.registration']
                vals ={}
                if event_id:
                    vals['title'] = kwarg['title']
                    vals['name'] = kwarg['name']
                    vals['last_name'] = kwarg['lastname']
                    vals['designation']= kwarg['designation']
                    vals['email']= kwarg['email']
                    vals['mobile']= kwarg['mobile']
                    vals['company_name']= kwarg['company_name']
                    vals['company_website']= kwarg['company_website']
                    vals['city_or_town']= kwarg['city_or_town']
                    vals['state_or_province']= kwarg['state_or_province']
                    vals['country_id']= int(kwarg['country'])
                    vals['event_id']=  event_id.id
                    vals['attendee_type_id']=14
                    attemdee_id=attendee.sudo().create(vals)
                    print(event_id.visitors_urls)

                    # pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                    #         'techfuge_customisation.report_visitor_badge', attemdee_id.id)
                    # pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
                    return request.redirect(str(event_id.sudo().visitors_urls)+"&successful=True")
            return request.redirect(str(event_id.sudo().visitors_urls)+"&successful=True")
    @http.route('/create/visit/badge/onsite', type='http', auth='none', csrf=False)
    def create_visit_badge_on_site(self,**kwarg):
        if 'token' in kwarg.keys():
            success =False
            event_id = request.env['event.event'].sudo().search([('event_key','=',kwarg['token'])])
            if 'successful' in kwarg:
                success = True
            if event_id.is_onsite:
                country_ids = request.env['res.country'].sudo().search([])
                if event_id:

                    return request.render("techfuge_exhibitor_customisation.visit_badge_printing_qr_code", {'event_id':event_id,'country_ids':country_ids,'successful':success})
                else:
                    return request.redirect("/")
            else:
                return request.redirect("/")

        else:
            return request.redirect("/")



    @http.route('/create/exhibitor/badge/onsite', type='http', auth='none', csrf=False)
    def create_exhibitor_badge_on_site(self,**kwarg):
            print(kwarg)
            contract = request.env['exhibitor.contract'].sudo().search([('id', '=', int(kwarg['id']))])
            if contract.event_id.is_onsite:
                attendee_vals={
                    'attendee_type_id': request.env.ref('techfuge_customisation.attendee_type_data_exhibitor').id,
                    'title':kwarg['title'],
                    'name':kwarg['firstName'],
                    'last_name':kwarg['lastName'],
                    'designation':kwarg['designation'],
                    'mobile':kwarg['mobile'],
                    'email':kwarg['email'],
                    'source_of_registration': 'from_website',
                    'event_id': contract.event_id.id,
                    'exhibitor_contract_id': contract.id,
                    'phone': contract.landline,
                    'company_name': contract.company_name,
                    'company_address': contract.company_address,
                    'company_website': contract.partner_id.website if contract.partner_id else False,
                    'city_or_town': contract.partner_id.city if contract.partner_id else False,
                    'state_or_province': contract.partner_id.state_id.name if  contract.partner_id.state_id else False,
                    'country_id': contract.partner_id.country_id.id if contract.partner_id  else False
                }
                request.env['event.registration'].sudo().create(attendee_vals)
                return request.redirect(contract.attendee_registration_link)
            else:
                return request.redirect("/")
    @http.route('/web/exhibitor/badge/qrcode', type='http', auth='none', csrf=False)
    def download_exhibitor_badge_on_site(self,**kwarg):
        if 'id' in kwarg.keys():
            pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'techfuge_customisation.report_visitor_badge', int(kwarg['id']))
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/create/exhibitor/attendee', type='http', auth='none', csrf=False)
    def create_exhibitor_badge_from_qrcode(self, **kwarg):
        contract = request.env['exhibitor.contract'].sudo().search([('authentication_token','=',str(kwarg['token']))])
        if contract.event_id.is_onsite:
            return request.render("techfuge_exhibitor_customisation.exhibitor_badge_printing_qr_code", {'contract':contract})
        else:
            return request.redirect("/")
