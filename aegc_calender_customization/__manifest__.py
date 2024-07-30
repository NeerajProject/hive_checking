# -*- coding: utf-8 -*-
{
    'name': "Calender Customization",

    'summary': """
       Calender Customization """,

    'description': """
      Calender Customization
    """,

    'author': "Tefuge Business Solutions",
    'website': "https://www.tecfuge.com",


    'category': 'Uncategorized',
    'version': '0.1',

    'depends':  ['base','calendar','appointment','membership','product','align_equesta_members','report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'report/calender_event.xml',
        'security/default_search_group_screen.xml',
        'view/appointment_type_timestamp.xml',
        'view/calendar_event.xml',
        'view/calender_type.xml',
        'view/product_template.xml',
        'wizard/calender_event_report.xml',
        'view/golf_event_create.xml',
        'data/ir_seqence.xml'
],    'assets': {

        'web.assets_backend': [
            'aegc_calender_customization/static/lib/action_manager.js',
            'aegc_calender_customization/static/xml/AegcContainerTables.xml',
            'aegc_calender_customization/static/xml/aegc_booking_backend.xml',
            'aegc_calender_customization/static/js/aegc_booking_backend.js',
            'aegc_calender_customization/static/xml/widget/popup_widget_available_slots.xml',
            'aegc_calender_customization/static/lib/popup_widget_available_slots.js',
            'aegc_calender_customization/static/lib/popup_widget_available_slots_update.js'

        ]
}

}
