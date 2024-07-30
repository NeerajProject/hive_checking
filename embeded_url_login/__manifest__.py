# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Login With Embedded Url',
    'version' : '1.2',
    'summary': ' Embedded  Login Url',
    'sequence': 10,
    'description': """ Embedded  Login Url   """,
    'depends' : ['web','base','crm'],
    'data': [
    'view/login_page_redirect.xml',
'view/custom_login_form.xml',
 'view/res_uses.xml'   ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
