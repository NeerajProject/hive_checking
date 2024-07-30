# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo import _


class SaleExhibitorPortal(portal.CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/more_info'], type='http', auth="public", methods=['POST'], website=True)
    def portal_quote_decline(self, order_id, access_token=None, more_information=None, **kwargs):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if order_sudo and more_information:
            order_sudo.with_user(order_sudo.user_id.id).sudo().write({
                'state': 'review_quote'
            })

            author_id = order_sudo.partner_id.id if order_sudo.partner_id else False
            email_from = None
            if author_id:
                email_from = order_sudo.partner_id.email_formatted if order_sudo.partner_id.email else None

            message_post_args = dict(
                body=more_information,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                author_id=author_id,
                email_from=email_from
            )

            order_sudo.with_context(mail_create_nosubscribe=True).message_post(**message_post_args)

        redirect_url = order_sudo.get_portal_url()

        return request.redirect(redirect_url)
