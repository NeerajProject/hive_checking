# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Notification Pannel',
    'version' : '1.2',
    'summary': ' Branding Pannel',
    'sequence': 10,
    'description': """ Embedded  Login Url   """,
    'depends' : ['web','base','crm','mail','techfuge_exhibitor_customisation'],
    'data': [

            'view/portal_activities.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
