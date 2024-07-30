import json
import logging

from odoo.addons.web.controllers.session import Session
import odoo
import odoo.modules.registry
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _

from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url
from odoo.addons.web.controllers.home import Home as WebHome
# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {'db', 'login', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}
LOGIN_SUCCESSFUL_PARAMS = set()



class Home(WebHome):

    @http.route([   '/redirect'], type='http', auth='user', website=True)
    def redirect_to_portal_page(self, **post):
        if request.env.user.has_group('base.group_portal'):
            return request.redirect("/exhibitor_dashboard")
        else:
            return request.redirect("/web")

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        print(kw)
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # simulate hybrid auth=user/auth=public, despite using auth=none to be able
        # to redirect users when no db is selected - cfr ensure_db()
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        if 'token'  in kw.keys():
            if request.httprequest.method == 'POST':
                try:
                    uid = request.session.authenticate(request.db, kw['token'], False,token=True)
                    request.params['login_success'] = True
                    return request.redirect(self._login_redirect(uid, redirect=redirect))
                except odoo.exceptions.AccessDenied as e:
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                    else:
                        values['error'] = e.args[0]
            else:
                if 'error' in request.params and request.params.get('error') == 'access':
                    values['error'] = _('Only employees can access this database. Please contact the administrator.')

            if 'login' not in values and request.session.get('auth_login'):
                values['login'] = request.session.get('auth_login')

            if not odoo.tools.config['list_db']:
                values['disable_database_manager'] = True
            values['login'] =kw['token']
            response = request.render('embeded_url_login.login', values)
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return response
        else:
            if request.httprequest.method == 'POST':
                try:
                    uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                    request.params['login_success'] = True
                    return request.redirect(self._login_redirect(uid, redirect=redirect))
                except odoo.exceptions.AccessDenied as e:
                    if e.args == odoo.exceptions.AccessDenied().args:
                        values['error'] = _("Wrong login/password")
                    else:
                        values['error'] = e.args[0]
            else:
                if 'error' in request.params and request.params.get('error') == 'access':
                    values['error'] = _('Only employees can access this database. Please contact the administrator.')

            if 'login' not in values and request.session.get('auth_login'):
                values['login'] = request.session.get('auth_login')

            if not odoo.tools.config['list_db']:
                values['disable_database_manager'] = True
            response = request.render('web.login', values)
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return response



