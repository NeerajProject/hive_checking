# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Branding Pannel',
    'version' : '1.1',
    'summary': ' Branding Pannel',
    'sequence': 10,
    'description': """ Embedded  Login Url   """,
    'depends' : ['web','base','crm','techfuge_exhibitor_customisation','portal','web_domain_field'],
    'data': [
        'security/ir.model.access.csv',
        'view/template/floor_plan.xml',
        'view/furnitures_branding_type.xml',
        'view/res_country_code_master.xml',
        'view/template/default_structure_change/default_structure_change.xml',
        'view/template/floor_plan_suggestions.xml',
        'view/template/floor_plan_stands.xml',
        'view/template/branding_pannel.xml',
        'view/accessories_branding_type.xml',
        'view/booth_design_line.xml',
        'view/exhibitor_contract.xml',
        'view/contract_floor_plan.xml',
        'data/activity_type.xml',
        'view/exhibitor_branding_panel_report.xml',
        'view/report_of_floor_plan.xml',
        'view/exhibitor_contract_branding_panel.xml',
        'view/branding_panel_badge.xml',
        'view/booth_design_type.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'brand_pannel_hive/static/src/js/branding_panel.js',
       'brand_pannel_hive/static/src/css/style.css'

        ]},
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
