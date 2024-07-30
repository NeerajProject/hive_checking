# -*- coding: utf-8 -*-

import json
import logging
import requests
import base64
from odoo import fields
from odoo import http
from odoo.http import request, Response
from odoo.exceptions import Warning
from datetime import datetime


_logger = logging.getLogger(__name__)


class VisitorRegistrationController(http.Controller):
    @http.route('/badge/download', type='http', auth='none', csrf=False, website=True)
    def download_badge_from_email(self, **kwarg):
        if 'id' in kwarg.keys():
            pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'techfuge_customisation.action_report_visitor_badge', int(kwarg['id']))
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)


    @http.route('/get_visitor_data_from_form', type='http', auth='none', csrf=False)
    def get_visitor_data_from_form(self, **kwarg):

        _logger.warning(kwarg)

        data = kwarg
        attendee_vals = {}
        user = request.env.ref('base.user_admin')
        event_registration_obj = request.env['event.registration'].sudo()
        event = False
        attendee_full_name = ''

        try:
            if 'title' in data:
                attendee_vals['title'] = str(data['title'])
                attendee_full_name += str(data['title']) + ' '

            if 'first_name' in data:
                attendee_vals['name'] = str(data['first_name'])
                attendee_full_name += str(data['first_name']) + ' '

            if 'last_name' in data:
                attendee_vals['last_name'] = str(data['last_name'])
                attendee_full_name += str(data['last_name'])

            if 'designation' in data:
                attendee_vals['designation'] = str(data['designation'])

            if 'business_email' in data:
                attendee_vals['email'] = str(data['business_email'])

            if 'mobile' in data:
                attendee_vals['mobile'] = str(data['mobile'])

            if 'company_name' in data:
                attendee_vals['company_name'] = str(data['company_name'])

            if 'company_website' in data:
                attendee_vals['company_website'] = str(data['company_website'])

            if 'company_address' in data:
                attendee_vals['company_address'] = str(data['company_address'])

            if 'city' in data:
                attendee_vals['city_or_town'] = str(data['city'])

            if 'state' in data:
                attendee_vals['state_or_province'] = str(data['state'])

            if 'country' in data:
                country = request.env['res.country'].sudo().search(
                    ['|', ('name', '=', str(data['country'])), ('wordpress_country_ref', '=', str(data['country']))],
                    limit=1)
                if country:
                    attendee_vals['country_id'] = country.id
                else:
                    attendee_vals['country_id'] = request.env.ref('base.ae').id

            if 'landline_number' in data:
                attendee_vals['phone'] = str(data['landline_number'])

            if 'nature_of_business' in data:
                nature_of_business_rec = request.env['event.business.nature'].sudo().search(
                    [('name', 'ilike', str(data['nature_of_business']))], limit=1)
                if nature_of_business_rec:
                    attendee_vals['nature_of_business_id'] = nature_of_business_rec.id
                else:
                    attendee_vals['nature_of_business_id'] = request.env.ref(
                        'techfuge_customisation.business_nature_data_chain_stores').id

            if 'purpose_of_visit' in data:
                purpose_of_visits = str(data['purpose_of_visit']).split(',') if data['purpose_of_visit'] else []

                purpose_of_visit_list = []

                for purpose in purpose_of_visits:
                    purpose_of_visit_rec = request.env['event.visit.purpose'].sudo().search(
                        [('name', 'ilike', purpose)], limit=1)
                    if purpose_of_visit_rec:
                        purpose_of_visit_list.append(purpose_of_visit_rec.id)

                if purpose_of_visit_list:
                    attendee_vals['purpose_of_visit_ids'] = [(6, 0, purpose_of_visit_list)]
                else:
                    purpose_of_visit = request.env.ref(
                        'techfuge_customisation.visit_purpose_data_meet_existing_supplier')
                    attendee_vals['purpose_of_visit_ids'] = [(6, 0, purpose_of_visit.ids)]

            if 'how_did_you_come_to_hive' in data:
                source_of_knowledge_rec = request.env['event.knowledge.source'].sudo().search(
                    [('name', 'ilike', str(data['how_did_you_come_to_hive']))], limit=1)
                if source_of_knowledge_rec:
                    attendee_vals['source_of_knowledge_id'] = source_of_knowledge_rec.id
                else:
                    attendee_vals['source_of_knowledge_id'] = request.env.ref(
                        'techfuge_customisation.knowledge_source_data_meet_invitation_by_show_organizer').id

            if 'what_best_describe_your_role' in data:
                role_description_list = list(
                    dict(event_registration_obj._fields['role_description'].selection).keys())
                if role_description_list:
                    if str(data['what_best_describe_your_role']) in role_description_list:
                        attendee_vals['role_description'] = str(data['what_best_describe_your_role'])
                    else:
                        attendee_vals['role_description'] = role_description_list[0]

            if 'size_of_enterprise' in data:
                no_of_stores_list = list(
                    dict(event_registration_obj._fields['no_of_stores'].selection).keys())
                if no_of_stores_list:
                    if str(data['size_of_enterprise']) in no_of_stores_list:
                        attendee_vals['no_of_stores'] = str(data['size_of_enterprise'])
                    else:
                        attendee_vals['no_of_stores'] = no_of_stores_list[0]

            if 'annual_revenue_enterprise' in data:
                annual_revenue_enterprise_list = list(
                    dict(event_registration_obj._fields['annual_revenue_enterprise'].selection).keys())
                if annual_revenue_enterprise_list:
                    if str(data['annual_revenue_enterprise']) in annual_revenue_enterprise_list:
                        attendee_vals['annual_revenue_enterprise'] = str(data['annual_revenue_enterprise'])
                    else:
                        attendee_vals['annual_revenue_enterprise'] = annual_revenue_enterprise_list[0]

            if 'product_categories_interested' in data:
                categories = str(data['product_categories_interested']).split(',') if data[
                    'product_categories_interested'] else []

                interested_categories_list = []

                for category in categories:
                    product_categories_interested_rec = request.env['interested.product.categories'].sudo().search(
                        [('name', 'ilike', category)], limit=1)
                    if product_categories_interested_rec:
                        interested_categories_list.append(product_categories_interested_rec.id)

                if interested_categories_list:
                    attendee_vals['interested_product_categories_ids'] = [(6, 0, interested_categories_list)]
                else:
                    interested_category = request.env.ref(
                        'techfuge_customisation.interested_product_categories_data_living_rooms')
                    attendee_vals['interested_product_categories_ids'] = [(6, 0, interested_category.ids)]

            if 'first_visit_exhibition' in data:
                attendee_vals['first_visit_exhibition'] = str(data['first_visit_exhibition'])

            if 'event_reference' in data:
                event = request.env['event.event'].sudo().search([('event_ref_no', '=', str(data['event_reference']))],
                                                                 limit=1)
                if event:
                    attendee_vals['event_id'] = event.id

            if 'attendee_type' in data:
                attendee_type = str(data['attendee_type'])
                attendee_type_id = False
                if attendee_type == 'STD':
                    if 'no_of_stores' in attendee_vals and 'annual_revenue_enterprise' in attendee_vals:
                        if attendee_vals['no_of_stores'] == '5-10' or attendee_vals['no_of_stores'] == '10 or more':
                            attendee_type_id = request.env.ref('techfuge_customisation.attendee_type_data_vip_buyer')
                        elif attendee_vals['annual_revenue_enterprise'] == 'Annual turnover $10-50 ML' or \
                                attendee_vals['annual_revenue_enterprise'] == 'Annual turnover over $50 ML':
                            attendee_type_id = request.env.ref('techfuge_customisation.attendee_type_data_vip_buyer')
                        else:
                            attendee_type_id = request.env.ref('techfuge_customisation.attendee_type_data_buyer')
                elif attendee_type == 'VIP':
                    attendee_type_id = request.env.ref('techfuge_customisation.attendee_type_data_hosted_vip_buyer')
                elif attendee_type == 'EXH':
                    attendee_type_id = request.env.ref('techfuge_customisation.attendee_type_data_exhibitor')

                attendee_type_rec = request.env['event.attendee.type'].sudo().browse(attendee_type_id.id)
                if attendee_type_rec:
                    attendee_vals['attendee_type_id'] = attendee_type_rec.id

            if attendee_full_name:
                attendee_vals['attendee_full_name'] = attendee_full_name

            attendee_vals['source_of_registration'] = 'from_website'

            if 'email' in attendee_vals:
                event_id = event.id if event else False
                attendee_full_name = attendee_vals[
                    'attendee_full_name'] if 'attendee_full_name' in attendee_vals else ''
                existing_rec = request.env['event.registration'].sudo().search([
                    ('event_id', '=', event_id),
                    ('email', '=', attendee_vals['email']),
                    ('name', '=', attendee_vals['name']),
                    ('last_name', '=', attendee_vals['last_name'])
                ], limit=1)
                if existing_rec:
                    existing_rec.write(attendee_vals)
                    existing_rec.send_visitor_registration_mail()
                    existing_rec.badge_sent = True
                    return json.dumps(existing_rec.id)
                else:
                    new_attendee_rec = request.env['event.registration'].with_user(user.id).sudo().with_context(
                        from_website_form=True).create(attendee_vals)
                    new_attendee_rec.send_visitor_registration_mail()
                    new_attendee_rec.badge_sent = True
                    return json.dumps(new_attendee_rec.id)
            else:
                new_attendee_rec = request.env['event.registration'].with_user(user.id).sudo().with_context(
                    from_website_form=True).create(attendee_vals)
                new_attendee_rec.send_visitor_registration_mail()
                new_attendee_rec.badge_sent = True
                return json.dumps(new_attendee_rec.id)

        except Exception as error:
            _logger.warning('Visitor Registration Failed Due to : %s', error)
            return 'ERROR'

    @http.route('/event_registration_details', type='http', auth='user', csrf=False, website=True)
    def portal_event_registration_details(self, **kwarg):
        values = {}
        event_id = False
        activity_locations = []
        exhibitor_list = []

        if kwarg:
            if 'attendee_id' in kwarg and kwarg['attendee_id']:
                attendee = request.env['event.registration'].sudo().browse(int(kwarg['attendee_id']))
                if attendee:
                    event_id = attendee.event_id
                    values['attendee'] = attendee

                    if attendee.exhibitor_contract_id:
                        exhibitor_contract = attendee.exhibitor_contract_id
                        values['is_food_coupon'] = request.env.user.hall_ids.activity_location_type_id.is_cafe
                        values['no_of_food_coupons'] = exhibitor_contract.no_of_food_coupons
                        values['used_food_coupons'] = exhibitor_contract.used_food_coupons

                    if event_id:
                        for location in event_id.activity_location_ids:
                            if location not in activity_locations:
                                activity_locations.append(location)

        if activity_locations:
            values['activity_locations'] = activity_locations

        sale_orders = request.env['sale.order'].sudo().search([('event_id', '=', event_id.id), ('state', '=', 'sale')])
        for order in sale_orders:
            if order.partner_id not in exhibitor_list:
                exhibitor_list.append(order.partner_id)

        if exhibitor_list:
            values['exhibitor_list'] = exhibitor_list

        return request.render("techfuge_customisation.portal_event_registration_details_template", values)

    @http.route('/submit/event_registration_details', type='http', auth='public', csrf=False, website=True)
    def portal_submit_event_registration_details(self, **kwarg):
        location_vals = {}
        user = request.env.user
        attendee_activity_id = False
        attendee_activity_exists = False
        attendee_activity_obj = request.env['event.attendee.activities'].sudo()
        if kwarg:
            if 'attendee_id' in kwarg and kwarg['attendee_id']:
                attendee = request.env['event.registration'].sudo().browse(int(kwarg['attendee_id']))
                if attendee:
                    location_vals['attendee_id'] = attendee.id
                    location_vals['event_id'] = attendee.event_id.id

                if 'attendee_activity_location' in kwarg and kwarg['attendee_activity_location']:
                    activity_location = request.env['event.activity.location'].sudo().search(
                        [('id', '=', int(kwarg['attendee_activity_location'])),
                         ('event_id', '=', attendee.event_id.id)])
                    if activity_location:
                        location_vals['name'] = activity_location.name
                        if activity_location.activity_location_type_id:
                            location_vals['activity_location_type_id'] = activity_location.activity_location_type_id.id
                            if activity_location.activity_location_type_id.attendee_group_id:
                                activity_group = activity_location.activity_location_type_id.attendee_group_id.name
                                location_vals['attendee_activity_group'] = activity_group

                if 'exhibitor_name' in kwarg:
                    location_vals['exhibitor_name'] = str(kwarg['exhibitor_name'])

                if 'stand_number' in kwarg:
                    location_vals['stand_number'] = str(kwarg['stand_number'])

                if location_vals:
                    location_vals.update({
                        'attendee_activity_datetime': fields.Datetime.now(),
                        'user_id': user.id
                    })

                    activity_location = request.env['event.activity.location'].sudo().search(
                        [('id', 'in', user.hall_ids.ids)])
                    attendee_activity = False
                    if activity_location:
                        attendee_activity = attendee_activity_obj.search([
                            ('name', '=', activity_location.name),
                            ('stand_number', '=', user.stand_ids.stand_number),
                            ('attendee_id', '=', attendee.id)
                        ])

                    exhibitor_contract = attendee.exhibitor_contract_id
                    if user.hall_ids.activity_location_type_id.is_cafe:
                        cafe_activities = False
                        if exhibitor_contract and exhibitor_contract.eligible_for_food_coupon:
                            if attendee_activity:
                                cafe_activities = attendee_activity.filtered(
                                    lambda a: a.attendee_activity_datetime.date() == fields.Date.today())
                            if exhibitor_contract.space_type_id.type == 'package':
                                if cafe_activities and len(cafe_activities) == 2:
                                    attendee_activity_exists = True
                            else:
                                if not exhibitor_contract.no_of_food_coupons:
                                    attendee_activity_exists = True
                                elif not exhibitor_contract.remaining_food_coupons:
                                    attendee_activity_exists = True
                                else:
                                    if cafe_activities and len(cafe_activities) == 2:
                                        attendee_activity_exists = True
                        else:
                            attendee_activity_exists = True

                    if not attendee_activity_exists:
                        attendee_activity_id = attendee_activity_obj.create(location_vals)
                        if exhibitor_contract.eligible_for_food_coupon and exhibitor_contract.no_of_food_coupons:
                            exhibitor_contract.used_food_coupons += 1
                    else:
                        return request.redirect('/event_registration_details/success')

        if attendee_activity_id:
            return request.redirect('/event_registration_details/success')

    @http.route('/event_registration_details/success', type='http', auth='public', csrf=False, website=True)
    def portal_submit_event_registration_details_success(self, **kwarg):
        return request.render("techfuge_customisation.portal_submit_event_registration_thanks_template", {})

    @http.route('/event_registration_details/fail', type='http', auth='public', csrf=False, website=True)
    def portal_submit_event_registration_details_fail(self, **kwarg):
        return request.render("techfuge_customisation.portal_submit_event_registration_fail_template", {})

    @http.route(['/attendee/badge/print'], type='http', auth="public", website=True, sitemap=False)
    def print_attendee_badge(self, **kwarg):
        if kwarg:
            if 'attendee_id' in kwarg and kwarg['attendee_id']:
                attendee = request.env['event.registration'].sudo().browse(int(kwarg['attendee_id']))
                if attendee:
                    if attendee.attendee_parent_type == 'exhibitor':
                        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                            'techfuge_exhibitor_customisation.action_report_exhibitor_badge',
                            [attendee.id])
                    elif attendee.attendee_parent_type == 'contractor':
                        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                            'techfuge_exhibitor_customisation.action_report_contractor_badge',
                            [attendee.id])
                    else:
                        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                            'techfuge_customisation.action_report_visitor_badge',
                            [attendee.id])
                    pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
                    return request.make_response(pdf, headers=pdfhttpheaders)
            else:
                return request.redirect('/')
