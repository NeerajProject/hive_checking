# -*- coding: utf-8 -*-
{
    'name': "Techfuge Customisations",
    'summary': """ Techfuge Customisations for Event Management""",
    'description': """
        Techfuge Customisations for Event Management
    """,
    'author': "Pragmatic",
    'website': "https://www.pragtech.co.in/",
    'category': 'Events',
    'version': '5.20',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account_accountant', 'crm', 'website', 'event_sale','hide_menu_user'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'reports/visitor_badge_report.xml',
        'data/mail_template_data.xml',
        # 'data/ir_cron_data.xml',
        'data/event_attendee_data.xml',
        'data/ir_action_data.xml',
        'views/attendee_group_views.xml',
        'views/activity_location_type_views.xml',
        'views/attendee_type_views.xml',
        'views/event_business_nature_views.xml',
        'views/event_visit_purpose_views.xml',
        'views/event_knowledge_source_views.xml',
        'views/interested_product_categories_views.xml',
        'views/event_attendee_activities_views.xml',
        'views/res_country_views.xml',
        'views/event_views.xml',
        'views/crm_lead_views.xml',
        'views/event_registration_views.xml',
        'views/sale_views.xml',
        'views/account_move_views.xml',
        'views/event_registration_detail_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'techfuge_customisation/static/src/scss/visitor_badge_report.scss',
        ],
        'web.assets_frontend': [
            'techfuge_customisation/static/src/js/event_registration_details.js',
        ],
    },
    'license': 'LGPL-3',
}
