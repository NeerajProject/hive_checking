
{
    'name' : 'Email Template for Portal Users',
    'version' : '1.0',
    'summary': 'Email Template for Portal Users',
    'sequence': 10,
    'description': """  Email Template for Portal Users  """,
    'depends' : ['web','base','event','techfuge_customisation','techfuge_exhibitor_customisation','brand_pannel_hive'],
    'data': [
        'data/action.xml',
        'data/contractor_email_template.xml',
        'data/mail_template_data.xml',
 'data/schedule_activity.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
