# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Agreement Customization',
    'version' : '1.1',
    'summary': ' Agreement Customization',
    'sequence': 10,
    'depends' : ['techfuge_exhibitor_customisation','event','techfuge_customisation','sale'],
    'data': [
        'security/ir.model.access.csv',
        'report/country_based_templates/exhibitor_hfs_2024_turkey.xml',
        'data/event_agreement_country.xml',
        'view/event_event.xml',
        'view/sale_order.xml',
        'report/terms_and_conditions/terms_and_conditions_iif_2023.xml',
        'report/terms_and_conditions/terms_and_conditions_hive_2024.xml',
        'report/hive_2024_report_template.xml',
        'report/iif_2023_report_template.xml',
        'report/template_hive_2024_template.xml',
        'report/hive_2024_report_template_turkey.xml',
        'report/terms_and_conditions/terms_and_conditions_hive_2024_turkey.xml',
        'view/event_agreement_country.xml'
  ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
