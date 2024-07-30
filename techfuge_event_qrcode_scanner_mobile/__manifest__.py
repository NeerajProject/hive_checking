# -*- coding: utf-8 -*-

{
    'name': 'Techfuge Event QR Code Scanner in Mobile',
    'category': 'Marketing/Events',
    'summary': 'Event QR Code Scanner in Mobile',
    'version': '1.0',
    'description': """ """,
    'author': "Pragmatic",
    'website': "https://www.pragtech.co.in/",
    'depends': ['techfuge_event_qrcode_scanner', 'barcodes_mobile'],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'techfuge_event_qrcode_scanner_mobile/static/src/js/**/*',
            'techfuge_event_qrcode_scanner_mobile/static/src/xml/**/*',
        ],
    }
}
