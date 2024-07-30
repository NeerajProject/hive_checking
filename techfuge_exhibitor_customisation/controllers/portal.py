# -*- coding: utf-8 -*-
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

_logger = logging.getLogger(__name__)


class ExhibitorDashboardController(http.Controller):

    @http.route('/my/payment/download', type='http', auth='user', csrf=False, website=True)
    def download_payment_reciept(self, **kwarg):
        if 'id' in kwarg.keys():
            pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'account.action_report_payment_receipt', int(kwarg['id']))
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/my/payment', type='http', auth='user', website=True, csrf=False)
    def get_payment_reiept(self, **kw):
        payments = request.env['account.payment'].sudo().search([      '|', ('partner_id', '=', request.env.user.partner_id.id),
            ('partner_id', '=', request.env.user.partner_id.parent_id.id)])
        values = {'payments': payments}

        return request.render("techfuge_exhibitor_customisation.portal_payment_reciept_details",
                              values)



    @http.route('/submit/hfs/shipment_documents', type='http', auth='user', website=True, csrf=False)
    def submit_shipment_document_submit(self, **kw):
        contract_id = request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['id']))])
        for rec in  contract_id.shipment_document_ids:
            rec.status = 'submitted'
        return request.redirect("/exhibitor_dashboard/shipment_details")
    @http.route('/submit/hfs/contractor_documents', type='http', auth='user', website=True, csrf=False)
    def submit_contractor_document_submit(self, **kw):
        contract_id = request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['id']))])
        for rec in  contract_id.contractor_document_ids:
            rec.status = 'submitted'
        return request.redirect("/exhibitor_dashboard/contractor_details")

    @http.route('/place_order/invoice/download', type='http', auth='user', csrf=False, website=True)
    def download_other_request_invoice(self, **kwarg):
        if 'id' in kwarg.keys():
            pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                'account.account_invoices', int(kwarg['id']))
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

        
    @http.route('/exhibitor_dashboard/other_requests/invoices', type='http', auth='user', csrf=False, website=True)
    def get_other_request_invoice(self, **kwarg):
           values = {}
           user = request.env.user

           if user.user_category == 'exhibitor':
               other_requests = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', user.partner_id.id), ('event_id', '=', user.event_id.id)])
               other_request_ids = other_requests.ids
               invoices = request.env['account.move'].search([('sale_id', 'in', other_request_ids)])
               values['invoice_count'] = len(invoices)
               values['invoices'] = invoices

           if user.user_category == 'contractor':
               other_requests = request.env['sale.order'].sudo().search(
                    [('partner_id', '=', user.partner_id.id), ('event_id', '=', user.event_id.id)])
               other_request_ids = other_requests.ids
               invoices = request.env['account.move'].search([('sale_id', 'in', other_request_ids)])
               values['invoice_count'] = len(invoices)
               values['invoices'] = invoices
           return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_other_requests_invoice",values)

    @http.route('/delete/attendee', type='http', auth='user', csrf=False, website=True)
    def delete_attendees(self, **kwarg):
        user = request.env.user
        if user.user_category == 'exhibitor':
            if 'id' in kwarg.keys():

                badge_id = request.env['event.registration'].sudo().search( [('id', '=', kwarg['id'])], limit=1)
                badge_id.unlink()
                return request.redirect('/exhibitor_dashboard/attendee_details')

    @http.route('/my/agreement', type='http', auth='user', csrf=False, website=True)
    def get_my_agreement(self, **kwarg):
        user = request.env.user
        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search(
                [ ('exhibitor_user_id', '=', user.id)], limit=1)
        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_agreement_finance", {'contract':contract})

    @http.route('/my/agreement/download',csrf=False, type='http', auth="user", website=True)
    def print_agreement_download(self,**kw):
        r = request.env['sale.order'].sudo().search([('id', '=', int(kw['id']))])
        agreement_template = r.event_id.exhibitor_email_template_id.report_template
        print(agreement_template)
        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(agreement_template, r.id)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    @http.route('/invitation_letter/download', csrf=False, type='http', auth="user", website=True)
    def print_invitation_letter(self, **kw):

        r = request.env['exhibitor.invitation.letter.request'].sudo().search([('id', '=', int(kw['id']))])
        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('techfuge_exhibitor_customisation.report_exhibitor_invitation_letter', r.id)
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
    @http.route('/submited/hotel_booking/request', type='http', auth='user', website=True, csrf=False)
    def submit_hotel_booking_request(self, **kw):
        contract_id = request.env['exhibitor.contract'].sudo().search([('id','=',int(kw['id']))])

        activity_id = request.env['mail.activity'].sudo().create({
            'res_name': contract_id.name + " Submitted HOTEL BOOKING",
            'is_portal_activity': True,
            'company_name': contract_id.company_name,
            'section': 'HOTEL BOOKING',
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': contract_id.partner_id.name + " Submitted HOTEL BOOKING",
            'user_id': request.env.user.id,
            'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id': contract_id.id
        })




        for rec in contract_id.hotel_request_ids:
            rec.status ='submit'
        return request.redirect('/exhibitor_dashboard/hotel_requests?hotel_booking_successful=True')

    @http.route('/exhibitor_dashboard', type='http', auth='user', website=True, csrf=False)
    def portal_exhibitor_dashboard(self, **kw):
        values = {}
        user = request.env.user
        quotation_count = request.env['sale.order'].sudo().search_count([
            ('partner_id', '=', user.partner_id.id),
            ('state', 'not in', ['sale', 'done', 'cancel'])
        ])
        proforma_count = request.env['sale.order'].sudo().search_count([
            ('partner_id', '=', user.partner_id.id),
            ('state', 'in', ['sale', 'done'])
        ])
        invoice_count = request.env['account.move'].sudo().search_count([
            ('partner_id', '=', user.partner_id.id)
        ])
        payment_receipt_count = request.env['account.payment'].sudo().search_count([
            '|', ('partner_id', '=', user.partner_id.id),
            ('partner_id', '=', user.partner_id.parent_id.id)
        ])

        contract = False
        attendee_domain = []
        values['is_exhibitor'] = request.env.user.user_category

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            attendee_domain = [('exhibitor_contract_id', '=', contract.id)]
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            attendee_domain = [('contractor_details_id', '=', contract.id)]

        if contract:
            attendees = request.env['event.registration'].sudo().search(attendee_domain)
            values.update({
                'contract': contract,
                'attendees': attendees,
                'quotation_count': quotation_count,
                'proforma_count': proforma_count,
                'invoice_count': invoice_count,
                'payment_receipt_count': payment_receipt_count,
            })
            if request.env.user.user_category == 'contractor':
                values['is_exhibitor'] =False
            else:
                values['is_exhibitor'] = True
            return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard", values)
        return request.redirect('/my/home')

    @http.route('/send/quick_mail', type='http', auth='user', csrf=False, website=True)
    def portal_send_quick_mail(self, **kwarg):
        user = request.env.user
        try:
            if kwarg:
                template = request.env.ref(
                    'techfuge_exhibitor_customisation.email_template_exhibitor_dashboard_quick_mail'
                )
                email_values = {
                    'email_from': user.partner_id.name + ' <' + user.partner_id.email + '>'
                }
                contract_id = False
                if 'contract_id' in kwarg:
                    contract_id = int(kwarg['contract_id'])

                if 'exh_quick_mailto' in kwarg:
                    email_values['email_to'] = str(kwarg['exh_quick_mailto'])

                if 'exh_quick_mail_subject' in kwarg:
                    email_values['subject'] = str(kwarg['exh_quick_mail_subject'])

                if 'exh_quick_mail_content' in kwarg:
                    email_values['body_html'] = kwarg['exh_quick_mail_content']

                if contract_id and email_values['body_html']:
                    template.with_user(user.id).sudo().send_mail(
                        contract_id, force_send=True, email_values=email_values
                    )

        except Exception as error:
            _logger.warning('Mail Sending Failed Due to : %s' % str(error))

        return request.redirect('/exhibitor_dashboard')

    @http.route('/exhibitor_dashboard/company_details', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_company_details(self, success=False, **kw):
        user = request.env.user

        halls = []
        stands = []
        package_options = []
        contract = False
        brand_name = False

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search(
                [ ('exhibitor_user_id', '=', user.id)], limit=1
            )
            brand_name = contract.brand_id.name
            for hall in contract.sale_order_id.hall_ids:
                if hall.name not in halls:
                    halls.append(hall.name)
            for stand in contract.sale_order_id.stand_ids:
                if stand.stand_id.stand_number not in stands:
                    stands.append(stand.stand_id.stand_number)
            for package in contract.sale_order_id.order_line:
                if package.product_template_id.name not in package_options:
                    package_options.append(package.product_template_id.name)
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('contractor_user_id', '=', user.id)
            ], limit=1)
        print('modes',contract)
        if 'exhibitor.contractor.details' == contract._name:
            if contract:
                contacts = request.env['res.partner'].sudo().search([('exhibitor_contract_id', '=', contract.exhibitor_contract_id.id)])
            else:
                contract = request.env['res.partner'].sudo().search([('exhibitor_contract_id', '=', -1)])
        else:
            if contract:
                contacts = request.env['res.partner'].sudo().search([('exhibitor_contract_id','=',contract.id)])
            else:
                contract = request.env['res.partner'].sudo().search([('exhibitor_contract_id','=',-1)])
        values = {
            'contract': contract,
            'contacts':contacts,
            'brand_name': brand_name,
            'halls': halls,
            'stands': stands,
            'package_options': package_options,
            'submission_success': success,
            'is_exhibitor':user.user_category
        }
        values['is_exhibitor'] = request.env.user.user_category

        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_company_details", values)

    @http.route('/exhibitor_dashboard/company_details/add_contact', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_add_contact(self, **kw):
        values = {}
        values['is_exhibitor'] = request.env.user.user_category
        values['country_code'] = request.env['res.country.code.master'].sudo().search([],order='country asc')
        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_add_contact", values)

    @http.route('/submit/contact_details', type='http', auth='user', csrf=False, website=True)
    def portal_submit_contact_details(self, **kwarg):
        user = request.env.user
        contact_vals = {
            'parent_id': user.partner_id.parent_id.id,
            'code_country': kwarg['country_code']
        }
        contact_name = ''
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search(
            [ ('exhibitor_user_id', '=', user.id)], limit=1
        )
        contact_vals['exhibitor_contract_id'] = exhibitor_contract.id

        exhibitor_contract.is_submission_mail_sent = True
        activity_id=request.env['mail.activity'].sudo().create({
            'is_portal_activity': True,
            'company_name': exhibitor_contract.company_name,
            'section': 'COMPANY DETAILS',
            'res_name': request.env.user.partner_id.name +" Added Contacts - "+str(kwarg['exh_contact_fname'])+" "+str(kwarg['exh_contact_lname']),
            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
            'summary': request.env.user.partner_id.name +" Added Contacts - "+str(kwarg['exh_contact_fname'])+" "+str(kwarg['exh_contact_lname']),
            'user_id' :  request.env.user.id,
            'res_model_id':request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
            'res_id':exhibitor_contract.id
        })



        print("end")
        try:
            if kwarg:
                if 'exh_contact_title' in kwarg.keys():
                    contact_title = str(kwarg['exh_contact_title']) + ' '
                    contact_name += contact_title
                    if contact_title == 'Ms.':
                        contact_title = 'Miss'
                    title_id = request.env['res.partner.title'].sudo().search([('shortcut', '=', contact_title)])
                    if title_id:
                        contact_vals['title'] = title_id.id

                contact_vals['exhibitor_contract_id'] = exhibitor_contract.id

                if   'code_country' in kwarg.keys():
                    contact_vals['code_country'] = kwarg['country_code']

                if 'exh_contact_fname' in kwarg.keys():
                    contact_name += str(kwarg['exh_contact_fname']) + ' '

                if 'exh_contact_lname' in kwarg.keys():
                    contact_name += str(kwarg['exh_contact_lname'])

                if contact_name:
                    contact_vals['name'] = contact_name

                if 'exh_contact_designation' in kwarg.keys():
                    contact_vals['function'] = str(kwarg['exh_contact_designation'])

                if 'exh_contact_mobile' in kwarg.keys():
                    if 'country_code' in kwarg.keys():
                        contact_vals['mobile'] = str(kwarg['country_code'])+ str(kwarg['exh_contact_mobile'])
                    else:
                        contact_vals['mobile'] = str(kwarg['exh_contact_mobile'])


                if 'exh_contact_email' in kwarg.keys():
                    contact_vals['email'] = str(kwarg['exh_contact_email'])

                if 'exh_contact_landline' in kwarg.keys():
                    contact_vals['phone'] = str(kwarg['exh_contact_landline'])

                if contact_vals and contact_vals['email']:
                    existing_contact = request.env['res.partner'].sudo().search([('email', '=', contact_vals['email'])])
                    if not existing_contact:
                        sale_user = exhibitor_contract.sale_order_id.user_id
                        partner_id = request.env['res.partner'].with_user(sale_user.id).sudo().create(contact_vals)

                        print(">>>>>> partner_id",partner_id)
                        partner_id.code_country = kwarg['country_code']
                        partner_id.exhibitor_contract_id =  exhibitor_contract.id

                        notification = 'New contact created by exhibitor %s' % user.partner_id.name
                        partner_id.message_post(
                            body=notification,
                            message_type="notification",
                            author_id=user.partner_id.id,
                            email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                            subtype_xmlid="mail.mt_comment"
                        )
                        activity_id.note = "<strong> Contact successfully created </strong><p> name :"+partner_id.name+"</p>"

                        return request.redirect('/exhibitor_dashboard/company_details?success=True')

        except Exception as error:
            error_message = 'Partner Creation Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message
            }
            values['is_exhibitor']=user.user_category

            return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_add_contact", values)

    @http.route('/exhibitor_dashboard/other_requests', type='http', auth='user', website=True, csrf=False)
    def portal_exhibitor_dashboard_other_requests(self, success=False, **kw):
        search = kw['search'] if 'search' in kw else ''
        values = {}
        user = request.env.user
        price_list = False
        contract = False

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            price_list = contract.sale_order_id.pricelist_id
            values['invoice_count'] = contract.exhibitor_invoice_count
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            price_list = contract.exhibitor_contract_id.sale_order_id.pricelist_id
            values['invoice_count'] = contract.contractor_invoice_count

        products = request.env['product.template'].sudo().search([('name', 'ilike', search),('is_place_order','=',True)])

        products_by_category = {}
        for product in products:
            if product.categ_id not in products_by_category:
                products_by_category[product.categ_id] = [product]
            else:
                products_by_category[product.categ_id].append(product)

        sorted_products_dict = {k: v for k, v in sorted(products_by_category.items(), key=lambda item: item[0].name)}

        values.update({
            'contract': contract,
            'search': search,
            'products_by_category': sorted_products_dict,
            'price_list': price_list,
            'other_request_count': len(contract.other_request_ids),
            'submission_success': success
        })
        values['is_exhibitor'] = user.user_category
        print("is_exhibitor")
        other_requests = request.env['sale.order'].sudo().search(
            [('partner_id', '=', user.partner_id.id), ('event_id', '=', user.event_id.id),
             ('is_other_request', '=', True)])
        other_request_ids = other_requests.ids
        # invoices = request.env['account.move'].search([('sale_id', 'in', other_request_ids)])
        invoices = request.env['account.move'].search(
            [('sale_id', 'in', other_request_ids), ('payment_state', 'not in', ['paid', 'in_payment'])])



        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_other_requests", values)

    @http.route('/add/other_request', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_add_other_request(self, product_id, **kw):
        values = {}
        user = request.env.user
        price_list = False
        exhibitor_contract_id = False
        contractor_details_id = False
        contract = False

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            exhibitor_contract_id = contract.id
            price_list = contract.sale_order_id.pricelist_id
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            contractor_details_id = contract.id
            price_list = contract.exhibitor_contract_id.sale_order_id.pricelist_id

        product = request.env['product.template'].sudo().browse([(int(product_id))])

        values.update({
            'contract': contract,
            'price_list': price_list,
            'other_request_count': len(contract.other_request_ids)
        })

        try:
            tax_id = product.taxes_id
            request.env['exhibitor.other.request'].sudo().create({
                'exhibitor_contract_id': exhibitor_contract_id,
                'contractor_details_id': contractor_details_id,
                'event_id': contract.event_id.id,
                'product_template_id': product.id if product else False,
                'product_uom_qty': 1,
                'price_unit': price_list._get_product_price(product, 1.0),
                'price_list_id': price_list.id,
                'tax_ids': tax_id.ids
            })




            return request.redirect('/exhibitor_dashboard/other_requests')

        except Exception as error:
            error_message = 'Request Submission Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message
            }
            values['is_exhibitor']=user.user_category

            return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_other_requests", values)

    @http.route('/exhibitor_dashboard/other_requests/details', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_other_requests_details(self, **kw):
        values = {}
        user = request.env.user
        price_list = False
        contract = False

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            price_list = contract.sale_order_id.pricelist_id
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            price_list = contract.exhibitor_contract_id.sale_order_id.pricelist_id

        amount_untaxed = sum(contract.other_request_ids.mapped('price_subtotal'))
        amount_tax = sum(contract.other_request_ids.mapped('price_tax'))
        amount_total = sum(contract.other_request_ids.mapped('price_total'))

        values.update({
            'contract': contract,
            'other_requests': contract.other_request_ids,
            'price_list': price_list,
            'amount_untaxed': amount_untaxed,
            'amount_tax': amount_tax,
            'amount_total': amount_total,
        })
        values['is_exhibitor'] = user.user_category
        return request.render(
            "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_other_requests_details", values
        )

    @http.route('/submit/other_requests', type='http', auth='user', website=True,csrf=False)
    def portal_exhibitor_dashboard_submit_other_requests(self, exhibitor_comment, **kw):
        user = request.env.user
        sales_order = False
        contract = False
        print(">>>>>>>>>>>>>>>>> ",user)





        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            sales_order = contract.sale_order_id
            contract.is_submission_mail_sent = True

        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            sales_order = contract.exhibitor_contract_id.sale_order_id

        try:
            fiscal_position_id =request.env['account.fiscal.position'].sudo().search([('is_place_order','=',True)],limit=1)
            sale_order = request.env['sale.order'].sudo().create({
                'exhibitor_contract_id': contract.id,
                'partner_id': contract.partner_id.id,
                'event_id': contract.event_id.id,
                'user_id': sales_order.user_id.id,
                'team_id': sales_order.team_id.id,
                'analytic_account_id': sales_order.analytic_account_id.id,
                'is_other_request': True,
                'exhibitor_other_request_comment': exhibitor_comment,
            })
            for other_req in contract.other_request_ids:
                request.env['sale.order.line'].sudo().create({
                    'product_template_id': other_req.product_template_id.id,
                    'product_id': other_req.product_template_id.product_variant_id.id,
                    'price_unit': other_req.price_unit,
                    'product_uom':other_req.product_template_id.uom_id.id,
                    'product_uom_qty': other_req.product_uom_qty,
                    'order_id': sale_order.id,
                    'price_subtotal': other_req.price_subtotal
                })

            print("start")
            print("ddd")
            activity_id = request.env['mail.activity'].sudo().create({
                'is_portal_activity': True,
                'company_name': contract.company_name,
                'section': 'Other Request',
                'res_name': sale_order.name + " Added Other Request",
               'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                'summary': sale_order.partner_id.name + " Added  Other Request",
                'user_id': request.env.user.id,
                'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_sale_order').id,
                'res_id': sale_order.id
            })

            print("end")



            contract.other_request_ids.unlink()
            print()
            if request.env.user.country_id.name =='United Arab Emirates':
                sale_order.sudo().with_context(is_other_request=True).action_confirm()
            else:
                sale_order.fiscal_position_id = fiscal_position_id
                sale_order.sudo().with_context(is_other_request=True).action_confirm()

            notification = 'Exhibitor %s placed an order' % user.partner_id.name
            contract.message_post(
                body=notification,
                message_type="notification",
                author_id=user.partner_id.id,
                email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                subtype_xmlid="mail.mt_comment"
            )
            other_req_invoice_id=sale_order.sudo()._create_invoices()
            print('/submit/other_requests',other_req_invoice_id)
            other_req_invoice_id.action_post()
            other_req_invoice_id.is_place_order_invoice = True
            for rec in other_req_invoice_id.invoice_line_ids:
                rec.product_uom_id = rec.product_id.uom_id

            return request.redirect('/exhibitor_dashboard/other_requests?success=True')

        except Exception as error:
            error_message = 'Request Submission Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message
            }
            values['is_exhibitor']=user.user_category
            return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_other_requests", values)

    @http.route('/update/other_requests', type='json', auth='user')
    def portal_exhibitor_dashboard_update_other_requests(self, other_request_id, input_quantity=False, **kw):
        other_request = request.env['exhibitor.other.request'].sudo().browse(int(other_request_id))


        if other_request:
            other_request.sudo().update({
                'product_uom_qty': input_quantity
            })
            return True
        return False

    @http.route('/exhibitor_dashboard/attendee_details', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_attendee_details(self, attendee_id=False, success=False, **kw):
        values = {}
        user = request.env.user
        contract = False
        space_type_id = False
        space_type = ''
        attendee_domain = []
        message = ''
        attendees = False
        remaining_badges = 0
        values['country_code'] = request.env['res.country.code.master'].sudo().search([],order='country asc')





        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            space_type_id = contract.space_type_id
            space_type = contract.space_type_id.type
            attendee_domain = [('exhibitor_contract_id', '=', contract.id)]
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            attendee_domain = [('contractor_details_id', '=', contract.id)]

        if contract:
            attendees = request.env['event.registration'].sudo().search(attendee_domain)

            used_badges = len(contract.badge_ids)
            remaining_badges = 0
            if contract.no_of_badges:
                remaining_badges = contract.no_of_badges - used_badges
            else:
                if space_type == 'non-package' or not space_type_id:
                    message = " Badge creatiob is on holdfor certain reason.Please contact us at exhibit@iiffglobal.com for further information."

        values.update({
            'contract': contract,
            'attendees': attendees,
            'countries': request.env['res.country'].sudo().search([]),
            'selected_attendee': request.env['event.registration'].sudo().browse(int(attendee_id)),
            'space_type': space_type,
            'no_of_badges': contract.no_of_badges,
            'remaining_badges_count': remaining_badges,
            'badge_info_message': message,
            'submission_success': success
        })
        values['is_exhibitor'] = user.user_category
        print("yessssssssssssssss")
        print(request.env['res.country.code.master'].sudo().search([]))

        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_attendee_details", values)

    @http.route('/submit/attendee_badge_request', type='http', auth='user', csrf=False, website=True)
    def portal_submit_attendee_badge_request(self, **kwarg):
        print("portal_submit_attendee_badge_request",kwarg)

        attendee_vals = {}
        user = request.env.user
        attendee_full_name = ''
        ir_attachment_obj = request.env['ir.attachment'].sudo()
        contract = False
        exhibitor_contract_id = False
        contractor_details_id = False
        attendee_type = False
        country_code = False
        if 'country_code' in kwarg.keys():
            country_code = int(kwarg['country_code'])
        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            print(">>>>>> user.user_category == 'exhibitor':")
            exhibitor_contract_id = contract.id
            attendee_type = request.env.ref('techfuge_customisation.attendee_type_data_exhibitor')
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            contractor_details_id = contract.id
            attendee_type = request.env.ref('techfuge_customisation.attendee_type_data_contractor')
            attendee_vals.update({
                'exhibitor_name': contract.exhibitor_contract_id.exhibitor_name
            })
        print(">>>>>>>>> checkpoint 2")
        try:
            if kwarg:
                if 'exh_attendee_title' in kwarg:
                    attendee_vals['title'] = str(kwarg['exh_attendee_title'])
                    attendee_full_name += attendee_vals['title'] + ' '

                if 'exh_attendee_first_name' in kwarg:
                    attendee_vals['name'] = str(kwarg['exh_attendee_first_name'])
                    attendee_full_name += attendee_vals['name'] + ' '

                if 'exh_attendee_last_name' in kwarg:
                    attendee_vals['last_name'] = str(kwarg['exh_attendee_last_name'])
                    attendee_full_name += attendee_vals['last_name']

                if 'exh_attendee_designation' in kwarg:
                    attendee_vals['designation'] = str(kwarg['exh_attendee_designation'])
                if 'country_code' in kwarg.keys():
                    attendee_vals['country_code'] = int(kwarg['country_code'])

                if 'exh_attendee_mobile' in kwarg:
                    attendee_vals['mobile'] =  str(kwarg['exh_attendee_mobile'])

                if 'exh_attendee_email' in kwarg:
                    attendee_vals['email'] = str(kwarg['exh_attendee_email'])

                if 'exh_attendee_passport' in kwarg:
                    passport_file = kwarg['exh_attendee_passport']
                    if passport_file.filename:
                        passport_attachment = ir_attachment_obj.create({
                            'name': passport_file.filename,
                            'datas': base64.encodebytes(passport_file.read()),
                            'type': 'binary',
                            'public': True
                        })
                        attendee_vals['passport_attachment_id'] = passport_attachment.id

                if 'exh_attendee_visa' in kwarg:
                    visa_file = kwarg['exh_attendee_visa']
                    if visa_file.filename:
                        visa_attachment = ir_attachment_obj.create({
                            'name': visa_file.filename,
                            'datas': base64.encodebytes(visa_file.read()),
                            'type': 'binary',
                            'public': True
                        })
                        attendee_vals['visa_attachment_id'] = visa_attachment.id

                if 'exh_attendee_air_ticket' in kwarg:
                    air_ticket_file = kwarg['exh_attendee_air_ticket']
                    if air_ticket_file.filename:
                        air_ticket_attachment = ir_attachment_obj.create({
                            'name': air_ticket_file.filename,
                            'datas': base64.encodebytes(air_ticket_file.read()),
                            'type': 'binary',
                            'public': True
                        })
                        attendee_vals['air_ticket_attachment_id'] = air_ticket_attachment.id

                print("check point 3")
                if attendee_vals and contract:

                    company_id = request.env['res.partner'].sudo().search([
                        ('name', '=', contract.company_name)
                    ], limit=1)

                    print("check point 4")


                    attendee_vals.update({
                        'attendee_type_id': attendee_type.id,
                        'source_of_registration': 'from_website',
                        'event_id': contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract_id,
                        'contractor_details_id': contractor_details_id,
                        'phone': contract.landline,
                        'company_name': contract.company_name ,
                        'company_address': contract.company_address,
                        'company_website': company_id.website if company_id else False,
                        'city_or_town': company_id.city if company_id else False,
                        'state_or_province': company_id.state_id.name if company_id and company_id.state_id else False,
                        'country_id': company_id.country_id.id if company_id and company_id.country_id else False
                    })

                    print(">>>>>>>>><<<<<<<<<<<<<< ----------  call the function -------->")
                    if 'selected_attendee' in kwarg and kwarg['selected_attendee']:
                        print("if 'selected_attendee' in kwarg and kwarg['selected_attendee']:")
                        attendee_domain = [('id', '=', int(kwarg['selected_attendee']))]
                    else:
                        attendee_domain = [
                            ('name', '=', attendee_vals['name']),
                            ('last_name', '=', attendee_vals['last_name']),
                            ('email', '=', attendee_vals['email'])
                        ]
                    existing_attendee = request.env['event.registration'].sudo().search(attendee_domain)
                    if existing_attendee:
                        existing_attendee.sudo().update(attendee_vals)
                        existing_attendee.send_visitor_registration_mail()
                        existing_attendee.badge_sent = True
                        redirect_url = '/exhibitor_dashboard/attendee_details'
                    else:
                        attendee_rec = request.env['event.registration'].sudo().create(attendee_vals)
                        attendee_rec.send_visitor_registration_mail()
                        attendee_rec.badge_sent = True
                        redirect_url = '/exhibitor_dashboard/attendee_details?success=True'
                    contract.is_submission_mail_sent = True
                    return request.redirect(redirect_url)

        except Exception as error:
            error_message = 'Attendee Registration Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message
            }
            values['is_exhibitor']=user.user_category

            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_attendee_details", values
            )

    def _prepare_portal_invitation_request_values(self):
        values = {
            'countries': request.env['res.country'].sudo().search([])
        }
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        if exhibitor_contract:
            exhibitor_attendees = request.env['event.registration'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            letter_requests = request.env['exhibitor.invitation.letter.request'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            values.update({
                'exhibitor_contract': exhibitor_contract,
                'exhibitor_attendees': exhibitor_attendees,
                'letter_requests': letter_requests,
                'travel_from_date': exhibitor_contract.event_id.checkin_date,
                'travel_till_date': exhibitor_contract.event_id.checkout_date
            })
        return values

    @http.route('/exhibitor_dashboard/invitation_letter_requests', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_invitation_letter_requests(self, success=False, **kw):
        values = self._prepare_portal_invitation_request_values()
        values.update({
            'submission_success': success
        })
        values['is_exhibitor'] = request.env.user.user_category

        return request.render(
            "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_invitation_letter_requests", values
        )

    @http.route('/submit/invitation_letter_request', type='http', auth='user', website=True, csrf=False)
    def portal_exhibitor_dashboard_submit_invitation_letter_request(self, **kwarg):
        letter_vals = {}
        values = self._prepare_portal_invitation_request_values()
        user = request.env.user

        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        exhibitor_contract.is_submission_mail_sent = True
        attendee = False
        try:
            if kwarg:
                if 'exh_letter_attendee' in kwarg:
                    letter_vals['attendee_id'] = int(kwarg['exh_letter_attendee'])
                    attendee = request.env['event.registration'].sudo().browse(int(kwarg['exh_letter_attendee']))

                if 'exh_letter_passport_no' in kwarg:
                    letter_vals['passport_number'] = kwarg['exh_letter_passport_no']

                if 'exh_letter_issue_date' in kwarg:
                    letter_vals['date_of_issue'] = kwarg['exh_letter_issue_date']

                if 'exh_letter_expiry_date' in kwarg:
                    letter_vals['date_of_expiry'] = kwarg['exh_letter_expiry_date']

                if 'exh_letter_birth_date' in kwarg:
                    letter_vals['date_of_birth'] = kwarg['exh_letter_birth_date']

                if 'exh_letter_country' in kwarg:
                    letter_vals['country_id'] = int(kwarg['exh_letter_country'])

                if 'exh_letter_from_date' in kwarg:
                    letter_vals['from_date'] = kwarg['exh_letter_from_date']

                if 'exh_letter_till_date' in kwarg:
                    letter_vals['till_date'] = kwarg['exh_letter_till_date']

                if 'exh_letter_no_of_days' in kwarg:
                    letter_vals['no_of_days'] = int(kwarg['exh_letter_no_of_days'])

                if letter_vals:
                    letter_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                    })

                    existing_request = request.env['exhibitor.invitation.letter.request'].sudo().search([
                        ('attendee_id', '=', letter_vals['attendee_id'])
                    ])

                    if existing_request:
                        values.update({
                            'error_message': 'Invitation letter already requested for this person'
                        })
                        values['is_exhibitor'] = request.env.user.user_category

                        return request.render(
                            "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_invitation_letter_requests",
                            values)

                    letter_request_id = request.env['exhibitor.invitation.letter.request'].sudo().create(letter_vals)

                    if letter_request_id:
                        pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
                            "techfuge_exhibitor_customisation.action_report_exhibitor_invitation_letter",
                            letter_request_id.id)[0]
                        pdf_data = base64.b64encode(pdf)
                        letter_attachment = request.env['ir.attachment'].sudo().create({
                            'name': 'Invitation Letter - %s.pdf' % letter_request_id.name,
                            'type': 'binary',
                            'datas': pdf_data,
                            'public': True
                        })
                        letter_request_id.letter_attachment_id = letter_attachment.id

                        notification = 'Exhibitor %s requested invitation letter for %s' % (
                            user.partner_id.name, attendee.attendee_full_name)
                        exhibitor_contract.message_post(
                            body=notification,
                            message_type="notification",
                            author_id=user.partner_id.id,
                            email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                            subtype_xmlid="mail.mt_comment"
                        )

                        print("starts ")
                        activity_id = request.env['mail.activity'].sudo().create({
                            'is_portal_activity': True,
                            'company_name': exhibitor_contract.company_name,
                            'section': 'INVITATION LETTER REQUEST',
                            'res_name': exhibitor_contract.name + " Submitted INVITATION LETTER REQUEST",
                           'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                            'summary': exhibitor_contract.partner_id.name + " Submitted INVITATION LETTER REQUEST",
                            'user_id': request.env.user.id,
                            'res_model_id': request.env.ref(
                                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                            'res_id': exhibitor_contract.id
                        })
                        print("end")
                    return request.redirect('/exhibitor_dashboard/invitation_letter_requests?success=True')

        except Exception as error:
            error_message = 'Invitation Letter Request Failed Due to : %s' % str(error)
            values.update({
                'error_message': error_message
            })
            values['is_exhibitor'] = request.env.user.user_category
            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_invitation_letter_requests", values
            )

    def _prepare_portal_hotel_booking_values(self):
        values = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        if exhibitor_contract:
            exhibitor_attendees = request.env['event.registration'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            hotel_requests = request.env['exhibitor.hotel.request'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            booked_rooms = len(exhibitor_contract.hotel_request_ids)
            remaining_rooms = 0
            if exhibitor_contract.allowed_hotel_rooms:

                remaining_rooms = 2*exhibitor_contract.allowed_hotel_rooms - booked_rooms

            values.update({
                'exhibitor_contract': exhibitor_contract,
                'exhibitor_attendees': exhibitor_attendees,
                'number_of_rooms':1,
                'hotel_requests': hotel_requests,
                'event': exhibitor_contract.event_id,
                'checkin_date': exhibitor_contract.event_id.checkin_date,
                'checkout_date': exhibitor_contract.event_id.checkout_date,
                'allowed_no_of_nights': exhibitor_contract.allowed_no_of_nights,
                'rate_per_additional_night': exhibitor_contract.event_id.rate_per_additional_night,
                'allowed_hotel_rooms': exhibitor_contract.allowed_hotel_rooms,
                'booked_rooms': booked_rooms,
                'remaining_rooms': remaining_rooms,
            })
        return values

    @http.route('/exhibitor_dashboard/hotel_requests', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_hotel_requests(self, success=False, **kw):
        values = self._prepare_portal_hotel_booking_values()
        values['hotel_booking_successful'] = False
        if 'hotel_booking_successful' in kw:
            values['hotel_booking_successful'] = True

        values.update({
            'submission_success': success
        })
        values['is_exhibitor'] = request.env.user.user_category
        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_hotel_requests", values)

    @http.route('/submit/hotel_booking_request', type='http', auth='user', csrf=False, website=True)
    def portal_submit_hotel_booking_request(self, **kwarg):

        hotel_vals = {}
        # hotel_vals['hotel_booking_successful'] = False

        values = self._prepare_portal_hotel_booking_values()
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id), ('event_id', '=', user.event_id.id)
        ], limit=1)

        exhibitor_contract.is_submission_mail_sent = True

        try:
            if kwarg:
                print(kwarg)
                if  'exh_hotel_arrival_date' in  kwarg:
                    hotel_vals['date_of_arrival_time'] = kwarg['exh_hotel_arrival_date']

                if 'room_id' in kwarg:
                    hotel_vals['room_id'] = kwarg['room_id']
                    hotel_vals['no_of_rooms'] = 1

                if 'exh_hotel_attendee' in kwarg:
                    hotel_vals['attendee_id'] = int(kwarg['exh_hotel_attendee'])

                if 'exh_hotel_checkin_date' in kwarg:
                    hotel_vals['checkin_date'] = kwarg['exh_hotel_checkin_date']

                if 'exh_hotel_checkout_date' in kwarg:
                    hotel_vals['checkout_date'] = kwarg['exh_hotel_checkout_date']

                if 'exh_hotel_additional_nights' in kwarg:
                    hotel_vals['additional_no_of_nights'] = kwarg['exh_hotel_additional_nights']

                if 'exh_hotel_additional_payment' in kwarg:
                    hotel_vals['additional_paid_amount'] = kwarg['exh_hotel_additional_payment']

                if 'exh_hotel_document' in kwarg:
                    hotel_file = kwarg['exh_hotel_document']
                    if hotel_file.filename:
                        hotel_attachment = request.env['ir.attachment'].sudo().create({
                            'name': hotel_file.filename,
                            'datas': base64.encodebytes(hotel_file.read()),
                            'type': 'binary',
                            'public': True
                        })
                        hotel_vals['hotel_attachment_id'] = hotel_attachment.id

                if hotel_vals:
                    hotel_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                    })
                    print('existing_booking',hotel_vals)
                    print('existing_booking  vals',kwarg)
                    existing_booking = request.env['exhibitor.hotel.request'].sudo().search(
                        [('attendee_id', '=', hotel_vals['attendee_id']),('exhibitor_contract_id','=',exhibitor_contract.id)])

                    if existing_booking:
                        values.update({
                            'error_message': 'Hotel already booked for this person'
                        })
                        values['is_exhibitor'] = request.env.user.user_category
                        return request.render(
                            "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_hotel_requests", values
                        )

                    hotel_request = request.env['exhibitor.hotel.request'].sudo().create(hotel_vals)


                    if 'additional_no_of_nights' in hotel_vals and hotel_vals['additional_no_of_nights']:
                        additional_night_product = request.env.ref(
                            'techfuge_exhibitor_customisation.product_product_hotel_booking_additional_night').sudo()

                        sale_order = request.env['sale.order'].sudo().create({
                            'partner_id': exhibitor_contract.partner_id.id,
                            'event_id': exhibitor_contract.event_id.id,
                            'user_id': exhibitor_contract.sale_order_id.user_id.id,
                            'team_id': exhibitor_contract.sale_order_id.team_id.id,
                            'analytic_account_id': exhibitor_contract.sale_order_id.analytic_account_id.id,
                            'hotel_request_id': hotel_request.id,
                            'order_line': [(0, 0, {
                                'name': additional_night_product.name,
                                'product_id': additional_night_product.id,
                                'product_uom_qty': hotel_vals['additional_no_of_nights'],
                                'product_uom': additional_night_product.uom_id.id,
                                'price_unit': additional_night_product.list_price,
                            })]
                        })

                        if sale_order:
                            hotel_request.sale_order_id = sale_order.id
                            sale_order.sudo().with_context(is_other_request=True).action_confirm()

                    notification = 'Exhibitor %s submitted the hotel request' % user.partner_id.name
                    exhibitor_contract.message_post(
                        body=notification,
                        message_type="notification",
                        author_id=user.partner_id.id,
                        email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                        subtype_xmlid="mail.mt_comment"
                    )
                    print("starts ")
                    activity_id = request.env['mail.activity'].sudo().create({
                        'res_name': exhibitor_contract.name + " Submitted HOTEL BOOKING",
                        'is_portal_activity': True,
                        'company_name': exhibitor_contract.company_name,
                        'section': 'HOTEL BOOKING',
                        'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                        'summary': exhibitor_contract.partner_id.name + " Submitted HOTEL BOOKING",
                        'user_id': request.env.user.id,
                        'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                        'res_id': exhibitor_contract.id
                    })
                    print("end")
                    return request.redirect('/exhibitor_dashboard/hotel_requests?success=True')

        except Exception as error:
            error_message = 'Hotel Request Submission Failed Due to : %s' % str(error)
            values.update({
                'error_message': error_message
            })
            values['is_exhibitor'] = request.env.user.user_category
            return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_hotel_requests", values)

    @http.route('/exhibitor_dashboard/uploaded_documents', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_uploaded_documents(self, success=False, **kw):
        values = {}
        user = request.env.user
        contract = False
        document_section_doc_types = []

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            document_section = request.env.ref(
                'techfuge_exhibitor_customisation.document_applicable_document_section'
            )
            document_section_doc_types = request.env['exhibitor.document.type'].sudo().search([
                ('document_applicable_ids', 'in', document_section.ids)
            ])
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            contractor_section = request.env.ref(
                'techfuge_exhibitor_customisation.document_applicable_contractor_section'
            )
            document_section_doc_types = request.env['exhibitor.document.type'].sudo().search([
                ('document_applicable_ids', 'in', contractor_section.ids)
            ])

        values.update({
            'contract': contract,
            'document_types': document_section_doc_types,
            'uploaded_documents': contract.uploaded_document_ids,
            'submission_success': success
        })
        values['is_exhibitor'] = request.env.user.user_category

        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_uploaded_documents", values)

    @http.route('/submit/uploaded_documents', type='http', auth='user', csrf=False, website=True)
    def portal_submit_uploaded_documents(self, **kwarg):
        print(">>>>>>>>>>>>>>>> called portal_submit_uploaded_documents",kwarg)
        document_vals = {}
        user = request.env.user
        contract = False
        exhibitor_contract_id = False
        contractor_details_id = False

        if user.user_category == 'exhibitor':
            contract = request.env['exhibitor.contract'].sudo().search([
                ('exhibitor_user_id', '=', user.id)
            ], limit=1)
            exhibitor_contract_id = contract.id
        elif user.user_category == 'contractor':
            contract = request.env['exhibitor.contractor.details'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            contractor_details_id = contract.id
            print(">> start",contract)

        try:
            if kwarg:
                if user.user_category == 'exhibitor':

                    if 'exh_document_type' in kwarg:
                        document_vals['document_type_id'] = int(kwarg['exh_document_type'])

                    if 'exh_document' in kwarg:
                        document_file = kwarg['exh_document']
                        if document_file.filename:
                            document_attachment = request.env['ir.attachment'].sudo().create({
                                'name': document_file.filename,
                                'datas': base64.encodebytes(document_file.read()),
                                'type': 'binary',
                                'public': True
                            })
                            document_vals['document_attachment_id'] = document_attachment.id

                    if 'exh_document_note' in kwarg:
                        document_vals['document_note'] = str(kwarg['exh_document_note'])

                    if document_vals:
                        document_vals.update({
                            'event_id': contract.event_id.id,
                            'exhibitor_contract_id': exhibitor_contract_id,
                            'contractor_details_id': contractor_details_id,
                        })

                        uploaded_document_id = request.env['exhibitor.uploaded.documents'].sudo().create(document_vals)

                        print("uploaded_document_id", uploaded_document_id.read())
                        activity_id = request.env['mail.activity'].sudo().create({
                            'res_name': user.partner_id.name + " Uploaded Documents ",
                            'is_portal_activity': True,
                            'company_name': contract.company_name,
                            'section': 'Documents',
                            'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                            'summary': user.partner_id.name + " Uploaded Documents "+str(uploaded_document_id.document_type_id.name)+"/"+str(uploaded_document_id.document_attachment_id.name),
                            'user_id': request.env.user.id,
                            'res_model_id': request.env.ref(
                                'techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                            'res_id': exhibitor_contract_id
                        })

                        notification = 'Exhibitor %s uploaded %s' % (
                            user.partner_id.name, uploaded_document_id.document_type_id.name
                        )
                        contract.message_post(
                            body=notification,
                            message_type="notification",
                            author_id=user.partner_id.id,
                            email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                            subtype_xmlid="mail.mt_comment"
                        )

                        contract.is_submission_mail_sent = True
                else:
                    if 'exh_document_type' in kwarg:
                          document_vals['document_type_id'] = int(kwarg['exh_document_type'])

                    if 'exh_document' in kwarg:
                        document_file = kwarg['exh_document']
                        if document_file.filename:
                            document_attachment = request.env['ir.attachment'].sudo().create({
                                    'name': document_file.filename,
                                    'datas': base64.encodebytes(document_file.read()),
                                    'type': 'binary',
                                    'public': True
                            })
                            document_vals['document_attachment_id'] = document_attachment.id

                        if 'exh_document_note' in kwarg:
                            document_vals['document_note'] = str(kwarg['exh_document_note'])

                        if document_vals:
                            document_vals.update({
                                'event_id': contract.event_id.id,
                                'exhibitor_contract_id': exhibitor_contract_id,
                                'contractor_details_id': contractor_details_id,
                            })

                            uploaded_document_id = request.env['exhibitor.uploaded.documents'].sudo().create(
                                document_vals)

                            notification = 'Exhibitor %s uploaded %s' % (
                                user.partner_id.name, uploaded_document_id.document_type_id.name
                            )
                            contract.message_post(
                                body=notification,
                                message_type="notification",
                                author_id=user.partner_id.id,
                                email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                                subtype_xmlid="mail.mt_comment"
                            )
                            print("yes reached " ,contract)


                return request.redirect('/exhibitor_dashboard/uploaded_documents?success=True')

        except Exception as error:
            error_message = 'Document Upload Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message
            }
            values['is_exhibitor'] = request.env.user.user_category

            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_uploaded_documents", values
            )

    def _prepare_portal_shipment_values(self):
        values = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)

        shipment_section = request.env.ref(
            'techfuge_exhibitor_customisation.document_applicable_shipment_section'
        )
        shipment_section_doc_types = request.env['exhibitor.document.type'].sudo().search([
            ('document_applicable_ids', 'in', shipment_section.ids)
        ])

        if exhibitor_contract:
            exhibitor_attendees = request.env['event.registration'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            shipment_details = request.env['exhibitor.shipment.details'].sudo().search(
                [('exhibitor_contract_id', '=', exhibitor_contract.id)])

            values.update({
                'exhibitor_contract': exhibitor_contract,
                'exhibitor_attendees': exhibitor_attendees,
                'document_types': shipment_section_doc_types,
                'uploaded_documents': exhibitor_contract.shipment_document_ids,
                'shipment_details': shipment_details
            })

        return values

    @http.route('/exhibitor_dashboard/shipment_details', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_shipment_details(self, success=False, **kw):
        values = self._prepare_portal_shipment_values()
        values.update({
            'submission_success': success
        })
        values['is_exhibitor'] = request.env.user.user_category

        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_shipment_details", values)

    @http.route('/submit/shipment_details', type='http', auth='user', csrf=False, website=True)
    def portal_submit_shipment_details(self, **kwarg):
        shipment_vals = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        values = self._prepare_portal_shipment_values()
        exhibitor_contract.is_submission_mail_sent = True
        try:
            mandatory_docs = request.env.ref(
                'techfuge_exhibitor_customisation.document_mandatory_shipment_section'
            )
            shipment_section_doc_types = request.env['exhibitor.document.type'].sudo().search([
                ('document_mandatory_ids', 'in', mandatory_docs.ids)
            ])
            for doc_type in shipment_section_doc_types:
                existing_doc = request.env['shipment.uploaded.documents'].sudo().search(
                    [('exhibitor_contract_id', '=', exhibitor_contract.id), ('document_type_id', '=', doc_type.id)])
                if not existing_doc:
                    relevant_docs_name = shipment_section_doc_types.mapped('name')
                    error_message = "Please add all the relevant documents !"
                    values.update({
                        'error_message': error_message,
                        'relevant_docs_name': relevant_docs_name,
                    })
                    values['is_exhibitor'] = request.env.user.user_category

                    return request.render(
                        "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_shipment_details", values
                    )

            if kwarg:

                if 'exh_shipment_volume' in kwarg:
                    shipment_vals['total_shipment_volume'] = float(kwarg['exh_shipment_volume'])

                if 'exh_shipment_allowed_cbm' in kwarg:
                    shipment_vals['allowed_cbm'] = float(kwarg['exh_shipment_allowed_cbm'])

                if 'exh_shipment_extra_cbm' in kwarg:
                    shipment_vals['extra_cbm'] = float(kwarg['exh_shipment_extra_cbm'])

                if 'exh_shipment_exc_charge' in kwarg:
                    shipment_vals['exceeding_charges'] = int(kwarg['exh_shipment_exc_charge'])

                if 'exh_shipment_add_charge' in kwarg:
                    shipment_vals['additional_charges'] = float(kwarg['exh_shipment_add_charge'])

                if 'exh_shipment_final_charge' in kwarg:
                    shipment_vals['final_charges'] = float(kwarg['exh_shipment_final_charge'])

                if 'exh_shipment_cartons' in kwarg:
                    shipment_vals['no_of_cartons'] = int(kwarg['exh_shipment_cartons'])

                if 'exh_shipment_net_weight' in kwarg:
                    shipment_vals['net_weight'] = float(kwarg['exh_shipment_net_weight'])

                if 'exh_shipment_gross_weight' in kwarg:
                    shipment_vals['gross_weight'] = float(kwarg['exh_shipment_gross_weight'])

                if 'exh_shipment_loading_port' in kwarg:
                    shipment_vals['port_of_loading'] = str(kwarg['exh_shipment_loading_port'])

                if 'exh_shipment_arrival_port' in kwarg:
                    shipment_vals['port_of_arrival_in_uae'] = str(kwarg['exh_shipment_arrival_port'])

                if shipment_vals:
                    shipment_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                    })

                    request.env['exhibitor.shipment.details'].sudo().create(shipment_vals)
                    notification = 'Exhibitor %s submitted the shipment details' % user.partner_id.name
                    exhibitor_contract.message_post(
                        body=notification,
                        message_type="notification",
                        author_id=user.partner_id.id,
                        email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                        subtype_xmlid="mail.mt_comment"
                    )

                    print("start")
                    print("sdmgb")
                    activity_id = request.env['mail.activity'].sudo().create({
                        'res_name': user.partner_id.name + " Submitted SHIPMENT DETAILS",
                        'is_portal_activity': True,
                        'company_name': exhibitor_contract.company_name,
                        'section': 'SHIPMENT DETAILS',
                       'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                        'summary': user.partner_id.name + " Submitted SHIPMENT DETAILS ",
                        'user_id': request.env.user.id,
                        'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                        'res_id': exhibitor_contract.id
                    })

                    print("end")


                    return request.redirect('/exhibitor_dashboard/shipment_details?success=True')

        except Exception as error:
            error_message = 'Shipment Details Submission Failed Due to : %s' % str(error)
            values = {
                'error_message': error_message,
                'exhibitor_contract': exhibitor_contract
            }
            values['is_exhibitor'] = request.env.user.user_category

            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_shipment_details", values
            )

    @http.route('/submit/shipment_uploaded_documents', type='http', auth='user', csrf=False, website=True)
    def portal_submit_shipment_uploaded_documents(self, **kwarg):
        print("shipment doc")
        document_vals = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)

        exhibitor_contract.is_submission_mail_sent = True

        try:
            if kwarg:

                if 'exh_shipment_document_type' in kwarg:
                    document_vals['document_type_id'] = int(kwarg['exh_shipment_document_type'])

                if 'exh_shipment_document_file' in kwarg:
                    document_file = kwarg['exh_shipment_document_file']



                    document_attachment = request.env['ir.attachment'].sudo().create({
                        'name': document_file.filename,
                        'datas': base64.encodebytes(document_file.read()),
                        'type': 'binary',
                        'public': True
                    })
                    document_vals['document_attachment_id'] = document_attachment.id

                if 'exh_shipment_document_note' in kwarg:
                    document_vals['document_note'] = str(kwarg['exh_shipment_document_note'])

                if document_vals:
                    document_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                    })

                    shipping_document_upload=request.env['shipment.uploaded.documents'].sudo().create(document_vals)
                    print(">>>>>>>>>>>> shipping ",shipping_document_upload.read())


                    activity_id = request.env['mail.activity'].sudo().create({
                        'is_portal_activity': True,
                        'company_name': exhibitor_contract.company_name,
                        'section': 'SHIPMENT DOCUMENTS  ',
                        'res_name': exhibitor_contract.partner_id.name + " Submitted SHIPMENT DOCUMENTS",
                       'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                        'summary': exhibitor_contract.partner_id.name + " Submitted SHIPMENT DOCUMENTS "+str(shipping_document_upload.document_type_id.name)+"/"+str(shipping_document_upload.document_attachment_id.name),
                        'user_id': request.env.user.id,
                        'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                        'res_id': exhibitor_contract.id
                    })

                    return request.redirect('/exhibitor_dashboard/shipment_details')

        except Exception as error:
            error_message = 'Unsupported Document Format  , Only (pdf /png/jpeg/) is allowed '
            values = {
                'error_message': error_message
            }
            values['is_exhibitor'] = request.env.user.user_category

            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_shipment_details", values
            )

    @http.route('/exhibitor_dashboard/contractor_details', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_contractor_details(self, success=False, **kw):
        values = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        if exhibitor_contract:
            exhibitor_attendees = request.env['event.registration'].sudo().search([
                ('exhibitor_contract_id', '=', exhibitor_contract.id)
            ])

            contractor_details = request.env['exhibitor.contractor.details'].sudo().search([
                ('exhibitor_contract_id', '=', exhibitor_contract.id)
            ])

            contractor_section = request.env.ref(
                'techfuge_exhibitor_customisation.document_applicable_contractor_section'
            )
            contractor_section_doc_types = request.env['exhibitor.document.type'].sudo().search([
                ('document_applicable_ids', 'in', contractor_section.ids)
            ])

            values.update({
                'exhibitor_contract': exhibitor_contract,
                'exhibitor_attendees': exhibitor_attendees,
                'countries': request.env['res.country'].sudo().search([]),
                'document_types': contractor_section_doc_types,
                'uploaded_documents': exhibitor_contract.contractor_document_ids,
                'contractor_details': contractor_details,
                'contract_purposes': request.env['contract.purpose'].sudo().search([]),
                'submission_success': success
            })

        values['country_code'] = request.env['res.country.code.master'].sudo().search([],order='country asc')

        values['is_exhibitor'] = request.env.user.user_category
        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_contractor_details", values)

    @http.route('/submit/contractor_details', type='http', auth='user', csrf=False, website=True)
    def portal_submit_contractor_details(self, **kwarg):
        contractor_vals = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('exhibitor_user_id', '=', user.id)
        ], limit=1)
        exhibitor_contract.is_submission_mail_sent = True
        try:
            if kwarg:

                if 'exh_contractor_title' in kwarg:
                    contractor_vals['title'] = str(kwarg['exh_contractor_title'])

                if 'exh_contractor_first_name' in kwarg:
                    contractor_vals['first_name'] = str(kwarg['exh_contractor_first_name'])

                if 'exh_contractor_last_name' in kwarg:
                    contractor_vals['last_name'] = str(kwarg['exh_contractor_last_name'])

                if 'exh_contractor_company_name' in kwarg:
                    contractor_vals['company_name'] = str(kwarg['exh_contractor_company_name'])

                if 'exh_contractor_mobile' in kwarg:
                    if 'country_code' in kwarg.keys():
                        contractor_vals['mobile'] = str(kwarg['country_code'])+str(kwarg['exh_contractor_mobile'])
                    else:
                        contractor_vals['mobile'] = str(kwarg['exh_contractor_mobile'])

                if 'exh_contractor_email' in kwarg:
                    contractor_vals['email'] = str(kwarg['exh_contractor_email'])

                if 'exh_contractor_landline' in kwarg:
                    contractor_vals['landline'] = str(kwarg['exh_contractor_landline'])

                if 'exh_contractor_designation' in kwarg:
                    contractor_vals['designation'] = str(kwarg['exh_contractor_designation'])

                if 'exh_contractor_company_address' in kwarg:
                    contractor_vals['company_address'] = str(kwarg['exh_contractor_company_address'])

                if 'exh_contractor_city' in kwarg:
                    contractor_vals['city_or_town'] = str(kwarg['exh_contractor_city'])

                if 'exh_contractor_state' in kwarg:
                    contractor_vals['state_or_province'] = str(kwarg['exh_contractor_state'])

                if 'exh_contractor_country' in kwarg:
                    if kwarg['exh_contractor_country']:
                        contractor_vals['country_id'] = int(kwarg['exh_contractor_country'])

                if 'exh_contractor_purpose' in kwarg:
                    if kwarg['exh_contractor_purpose']:
                        contractor_vals['contract_purpose_id'] = int(kwarg['exh_contractor_purpose'])

                if contractor_vals:
                    contractor_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                        'brand_id': exhibitor_contract.brand_id.id if exhibitor_contract.brand_id else False,
                    })

                    request.env['exhibitor.contractor.details'].with_user(
                        exhibitor_contract.sale_order_id.user_id.id).sudo().create(contractor_vals)
                    notification = 'Exhibitor %s submitted the contractor details' % user.partner_id.name
                    exhibitor_contract.message_post(
                        body=notification,
                        message_type="notification",
                        author_id=user.partner_id.id,
                        email_from="HIVE FURNITURE SHOW <exhibit@hivefurnitureshow.com>",
                        subtype_xmlid="mail.mt_comment"
                    )
                    return request.redirect('/exhibitor_dashboard/contractor_details?success=True')

        except Exception as error:
            error_message = 'Contractor Details Submission Failed Due to : %s', error
            values = {
                'error_message': error_message,
                'exhibitor_contract': exhibitor_contract
            }
            values['is_exhibitor'] = request.env.user.user_category
            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_contractor_details", values
            )

    @http.route('/submit/contractor_uploaded_documents', type='http', auth='user', csrf=False, website=True)
    def portal_submit_contractor_uploaded_documents(self, **kwarg):
        print("???????????",kwarg)
        document_vals = {}
        user = request.env.user
        exhibitor_contract = request.env['exhibitor.contract'].sudo().search([
            ('partner_id', '=', user.partner_id.id)
        ], limit=1)
        exhibitor_contract.is_submission_mail_sent = True
        try:
            if kwarg:

                if 'ehx_contractor_document_type' in kwarg:
                    document_vals['document_type_id'] = int(kwarg['ehx_contractor_document_type'])

                if 'ehx_contractor_document' in kwarg:
                    document_file = kwarg['ehx_contractor_document']
                    document_attachment = request.env['ir.attachment'].sudo().create({
                        'name': document_file.filename,
                        'datas': base64.encodebytes(document_file.read()),
                        'type': 'binary',
                        'public': True
                    })
                    document_vals['document_attachment_id'] = document_attachment.id

                if 'ehx_contractor_document_note' in kwarg:
                    document_vals['document_note'] = str(kwarg['ehx_contractor_document_note'])

                document_vals['contractor_id'] = int(kwarg['ehx_contractor_id'])

                if document_vals:
                    document_vals.update({
                        'event_id': exhibitor_contract.event_id.id,
                        'exhibitor_contract_id': exhibitor_contract.id,
                    })


                    countractor_documents=request.env['contractor.uploaded.documents'].sudo().create(document_vals)

                    activity_id = request.env['mail.activity'].sudo().create({
                        'is_portal_activity': True,
                        'company_name': exhibitor_contract.company_name,
                        'section': 'CONTRACTOR DOCUMENTS  ',
                        'res_name': exhibitor_contract.partner_id.name + " Submitted Contractor Documents",
                        'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                        'summary': exhibitor_contract.partner_id.name + "Submitted Contractor Documents " + str(
                            countractor_documents.document_type_id.name) + "/" + str(
                            countractor_documents.document_attachment_id.name),
                        'user_id': request.env.user.id,
                        'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                        'res_id': exhibitor_contract.id
                    })

                    return request.redirect('/exhibitor_dashboard/contractor_details')

        except Exception as error:
            error_message = 'Document Upload Failed Due to : %s', error
            values = {
                'error_message': error_message
            }
            values['is_exhibitor'] = request.env.user.user_category
            return request.render(
                "techfuge_exhibitor_customisation.portal_exhibitor_dashboard_contractor_details", values
            )

    @http.route('/exhibitor_dashboard/scan_badge', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_scan_badge(self, **kw):
        values = {}
        values['is_exhibitor'] = request.env.user.user_category
        return request.render("techfuge_exhibitor_customisation.portal_exhibitor_dashboard_scan_badge", values)

    @http.route('/delete/exhibitor_data', type='http', auth='user', website=True)
    def portal_exhibitor_dashboard_delete_data(self, record_id, model, **kw):
        redirect_url = '/exhibitor_dashboard'

        if model and record_id:
            record = request.env[model].sudo().browse(int(record_id))
            if record:

                if model == 'exhibitor.hotel.request':

                    redirect_url = '/exhibitor_dashboard/hotel_requests'
                elif model == 'exhibitor.uploaded.documents':

                    activity_id = request.env['mail.activity'].sudo().create({
                        'res_name': record.exhibitor_contract_id.exhibitor_name + " deleted Document " + record.document_type_id.name,
                        'is_portal_activity': True,
                        'company_name': record.exhibitor_contract_id.company_name,
                        'section': 'Document Upload',
                        'activity_type_id': request.env.ref('brand_pannel_hive.portal_users_activity').id,
                        'summary': record.exhibitor_contract_id.exhibitor_name + " deleted Document " + record.document_type_id.name,
                        'user_id': request.env.user.id,
                        'res_model_id': request.env.ref('techfuge_exhibitor_customisation.model_exhibitor_contract').id,
                        'res_id': record.exhibitor_contract_id.id
                    })
                    redirect_url = '/exhibitor_dashboard/uploaded_documents'
                elif model == 'exhibitor.shipment.details':
                    redirect_url = '/exhibitor_dashboard/shipment_details'
                elif model == 'shipment.uploaded.documents':
                    redirect_url = '/exhibitor_dashboard/shipment_details'
                elif model == 'exhibitor.contractor.details':
                    redirect_url = '/exhibitor_dashboard/contractor_details'
                elif model == 'contractor.uploaded.documents':

                    redirect_url = '/exhibitor_dashboard/contractor_details'
                elif model == 'exhibitor.invitation.letter.request':
                    redirect_url = '/exhibitor_dashboard/invitation_letter_requests'
                elif model == 'exhibitor.other.request':
                    redirect_url = '/exhibitor_dashboard/other_requests/details'

                record.unlink()
        return request.redirect(redirect_url)
