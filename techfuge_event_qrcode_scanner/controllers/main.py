# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

from odoo.addons.web.controllers.home import ensure_db, Home


class EventQRScanningHome(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super().web_login(*args, **kw)
        user = request.env.user
        if request.session.uid:
            if user._is_public() and user.event_id and user.hall_ids:
                return request.redirect_query('/exhibitor_dashboard/scan_badge')
        return response


class EventQRCode(http.Controller):

    @http.route(['/event/init_qrcode_interface'], type='json', auth="user")
    def init_qrcode_interface(self):
        event_id = request.env.user.event_id.id
        event = request.env['event.event'].browse(event_id).exists() if event_id else False
        if event:
            return {
                'name': event.name,
                'country': event.address_id.country_id.name,
                'city': event.address_id.city,
                'company_name': event.company_id.name,
                'company_id': event.company_id.id
            }
        else:
            return {
                'name': _('QR Code Scanner'),
                'country': False,
                'city': False,
                'company_name': request.env.company.name,
                'company_id': request.env.company.id
            }
