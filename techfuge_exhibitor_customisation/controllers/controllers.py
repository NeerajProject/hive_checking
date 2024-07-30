# -*- coding: utf-8 -*-

import json
import logging
import requests
import base64

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import Warning
from datetime import datetime

_logger = logging.getLogger(__name__)


class ExhibitorRegistrationController(http.Controller):

    @http.route('/get_crm_data_from_form', type='http', auth='none', csrf=False)
    def get_crm_data_from_form(self, **kwarg):
        data = kwarg
        _logger.warning(kwarg)

        crm_vals = {}
        user = request.env.ref('base.user_admin')
        lead_name = ''

        if 'title' in data:
            #custom code here
            title_dictionary = {'MS.': 'Ms.',
                                'MR.': 'Mr.',
                                'MRS.': 'Mrs.'}

            if data['title'] in title_dictionary.keys():
                rec_title = title_dictionary[data['title']]
            else:
                rec_title = data['title']
             #end
            # rec_title = data['title']
            if 'sqmf' in kwarg.keys():
                crm_vals['desired_area_in_sqm'] = kwarg['sqmf']
            crm_vals['title_abbr'] = rec_title
            if rec_title == 'Ms.':
                title = request.env['res.partner.title'].search([('shortcut', '=', 'Miss')], limit=1)
            else:
                title = request.env['res.partner.title'].search([('shortcut', 'ilike', rec_title)], limit=1)
            if title:
                crm_vals['title'] = title.id

        if 'first_name' in data:
            crm_vals['contact_name'] = str(data['first_name']).upper()

        if 'last_name' in data:
            crm_vals['last_name'] = str(data['last_name']).upper()

        if 'designation' in data:
            crm_vals['function'] = str(data['designation']).upper()

        if 'company_name' in data:
            crm_vals['partner_name'] = str(data['company_name']).upper()
            lead_name = str(data['company_name']).upper()

        if 'company_website' in data:
            crm_vals['website'] = str(data['company_website'])

        if 'company_address' in data:
            crm_vals['street'] = str(data['company_address'])

        if 'city' in data:
            crm_vals['city'] = str(data['city'])

        if 'country' in data:
            res_country = request.env['res.country'].sudo().search([('name', '=', str(data['country']))], limit=1)
            if res_country:
                crm_vals['country_id'] = res_country.id
                if 'state' in data:
                    res_state = request.env['res.country.state'].sudo().search([('name', '=', str(data['state']))],
                                                                               limit=1)
                    if res_state:
                        crm_vals['state_id'] = res_state.id

        if 'business_email' in data:
            crm_vals['email_from'] = str(data['business_email'])
            crm_vals['additional_email'] = str(data['business_email'])

        if 'mobile' in data:
            crm_vals['mobile'] = str(data['mobile'])

        if 'landline_number' in data:
            crm_vals['phone'] = str(data['landline_number'])

        if 'product_categories_interested' in data:
            crm_vals['product_categories'] = str(data['product_categories_interested'])

        if 'about_company' in data:
            crm_vals['about_exhibitor_company'] = str(data['about_company'])

        if 'communication_permission' in data:
            crm_vals['communication_permission'] = data['communication_permission']

        if 'brand' in data:
            brand = request.env['res.brand'].sudo().search([('name', '=', str(data['brand']))])
            if not brand:
                brand = request.env['res.brand'].sudo().create({
                    'name': str(data['brand'])
                })
            crm_vals['brand_id'] = brand.id if brand else False

        if 'event_reference' in data:
            event = request.env['event.event'].sudo().search([('event_ref_no', '=', str(data['event_reference']))],
                                                             limit=1)
            if event:
                crm_vals['event_id'] = event.id
                lead_name = event.name + ' -  ' + lead_name

                if event.analytic_account_id:
                    crm_vals['analytic_account_id'] = event.analytic_account_id.id

                if event.sales_person_id:
                    crm_vals['user_id'] = event.sales_person_id.id

                if event.sales_team_id:
                    crm_vals['team_id'] = event.sales_person_id.id

        if lead_name:
            crm_vals['name'] = lead_name

        crm_vals['source_of_registration'] = 'from_website'

        crm_rec = request.env['crm.lead'].with_user(user.id).sudo().create(crm_vals)

        return json.dumps(crm_rec.id)
