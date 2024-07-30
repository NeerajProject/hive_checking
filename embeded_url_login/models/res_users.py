
from odoo import api, models, _
from odoo.exceptions import ValidationError

import binascii
import contextlib
import datetime
import hmac
import ipaddress
import itertools
import json
import logging
import os
import time
from collections import defaultdict
from functools import wraps
from hashlib import sha256
from itertools import chain, repeat
from markupsafe import Markup
import hashlib

import babel.core
import pytz
from lxml import etree
from lxml.builder import E
from passlib.context import CryptContext
from psycopg2 import sql

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request, DEFAULT_LANG
from odoo.osv import expression
from odoo.service.db import check_super
from odoo.tools import is_html_empty, partition, collections, frozendict, lazy_property

_logger = logging.getLogger(__name__)

# Only users who can modify the user (incl. the user herself) see the real contents of these fields
USER_PRIVATE_FIELDS = []
MIN_ROUNDS = 350000
concat = chain.from_iterable

class ResUsers(models.Model):
    _inherit = "res.users"

    authentication_token = fields.Char(compute='compute_authentication_token',store=True)
    authentication_url = fields.Char(compute='compute_authentication_url')


    @api.depends('authentication_token')
    def compute_authentication_url(self):
        if self._origin:
            for rec in self:
                if rec.authentication_token:
                    rec.authentication_url= rec.get_base_url()+'/web/login?token='+rec.authentication_token
        else:
            self.authentication_url =False


    @api.depends('login')
    def compute_authentication_token(self):
        if self._origin:
            
            for rec in self._origin:
                if rec.login:
                    token = rec.login
                    rec.authentication_token= hashlib.sha1(token.encode()).hexdigest()
                else:
                    rec.authentication_token = False
        else:
            self.authentication_token = False

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        print("custom  based models")
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth(user=login):
                    user = self.search(self._get_login_domain(login), order=self._get_login_order(), limit=1)
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password, user_agent_env)
                    tz = request.httprequest.cookies.get('tz') if request else None
                    if tz in pytz.all_timezones and (not user.tz or not user.login_date):
                        # first login or missing tz -> set tz to browser tz
                        user.tz = tz
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise

        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)

        return user.id

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env,token=False):
        """Verifies and returns the user ID corresponding to the given
          ``login`` and ``password`` combination, or False if there was
          no matching user.
           :param str db: the database on which user is trying to authenticate
           :param str login: username
           :param str password: user password
           :param dict user_agent_env: environment dictionary describing any
               relevant environment attributes
        """
        print('token',token)

        if  password:
            uid = cls._login(db, login, password, user_agent_env=user_agent_env)
            if user_agent_env and user_agent_env.get('base_location'):
                with cls.pool.cursor() as cr:
                    env = api.Environment(cr, uid, {})
                    if env.user.has_group('base.group_system'):
                        # Successfully logged in as system user!
                        # Attempt to guess the web base url...
                        try:
                            base = user_agent_env['base_location']
                            ICP = env['ir.config_parameter']
                            if not ICP.get_param('web.base.url.freeze'):
                                ICP.set_param('web.base.url', base)
                        except Exception:
                            _logger.exception("Failed to update web.base.url configuration parameter")
            return uid

        else:

            if user_agent_env and user_agent_env.get('base_location'):
                with cls.pool.cursor() as cr:
                    cr.execute("SELECT id FROM res_users where authentication_token='" + login + "'")
                    uid = cr.dictfetchone()['id']
                    env = api.Environment(cr, uid, {})
                    if env.user.has_group('base.group_system'):
                        # Successfully logged in as system user!
                        # Attempt to guess the web base url...
                        try:
                            base = user_agent_env['base_location']
                            ICP = env['ir.config_parameter']
                            if not ICP.get_param('web.base.url.freeze'):
                                ICP.set_param('web.base.url', base)
                        except Exception:
                            _logger.exception("Failed to update web.base.url configuration parameter")
            return uid
