# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Branding Pannel Report',
    'version' : '1.1',
    'summary': ' Branding Pannel',
    'sequence': 10,
    'description': """ Embedded  Login Url   """,
    'depends' : ['web','base','brand_pannel_hive','techfuge_customisation','techfuge_exhibitor_customisation','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'report/branding_paper_formate.xml',
        'report/branding_panel_report_template.xml',
        'report/branding_info_exhibitor_contract.xml',
        'report/branding_panel_category_report_template.xml',
        'wizard/branding_panel_report.xml'

  ],

'assets': {
        'web.assets_backend': [
            'brand_pannel_report/static/src/js/action_manager.js'
        ]
    },


    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}