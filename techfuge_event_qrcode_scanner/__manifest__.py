# -*- coding: utf-8 -*-

{
    'name': "Techfuge Event QR Code Scanning",
    'summary': "Add QR code scanning feature to event management.",
    'version': '1.4',
    'description': """
        This module adds support for qr codes scanning to the Event management system.
    """,
    'author': "Pragmatic",
    'website': "https://www.pragtech.co.in/",
    'category': 'Marketing/Events',
    'depends': ['techfuge_exhibitor_customisation', 'event', 'event_barcode','hide_menu_user'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/attendee_registration_confirm_views.xml',
        'views/event_event_views.xml',
        'views/portal_layout_inherit_template.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'techfuge_event_qrcode_scanner/static/src/js/event_qrcode.js',
            'techfuge_event_qrcode_scanner/static/src/js/qr_scanning_form.js',
            'techfuge_event_qrcode_scanner/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            'https://rawgit.com/sitepoint-editors/jsqrcode/master/src/qr_packed.js',
            'techfuge_event_qrcode_scanner/static/src/js/exhibitor_dashboard_qrcode.js',
        ],
    }
}
