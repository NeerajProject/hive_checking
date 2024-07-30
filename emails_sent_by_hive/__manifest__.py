
{
    'name' : 'Email Sent by Events',
    'version' : '1.0',
    'summary': ' Email Sent by Events',
    'sequence': 10,
    'description': """ Email Sent by Events   """,
    'depends' : ['web','base','event','techfuge_customisation','techfuge_exhibitor_customisation'],
    'data': [
'view/event_event.xml',
        'view/mail_template.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
