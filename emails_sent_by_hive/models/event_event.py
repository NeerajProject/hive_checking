from odoo import api, fields, models, _
from datetime import timedelta


class Event(models.Model):
    _inherit = 'event.event'

    event_contractor_registration = fields.Many2one('mail.template',string="Contractor Registration: Dashboard",
                                                    domain=[('is_event_related_issue','=',True),
                                                            ('model','=','exhibitor.contractor.details')])

    event_exhibitor_confirmation = fields.Many2one('mail.template',string="Confirmation Mail to Exhibitor",
                                                   domain=[('is_event_related_issue','=',True),
                                                           ('model','=','exhibitor.contract')])

    event_exhibitor_mail_to_exhibitor = fields.Many2one('mail.template',string="Mail to Exhibitor",
                                                        domain=[('is_event_related_issue','=',True),
                                                                ('model','=','')])
    event_exhibitor_mail_to_planner = fields.Many2one('mail.template',string="Mail to Planner",
                                                      domain=[('is_event_related_issue','=',True),('model','=','crm.lead')])
    event_exhibitor_send_invoice_to_exhibitor = fields.Many2one('mail.template',string="Send Invoice to Exhibitor",
                                                                domain=[('is_event_related_issue','=',True),
                                                                        ('model','=','account.move')])

    event_exhibitor_pro_forma_to_exhibitor = fields.Many2one('mail.template',string="Send Pro-forma to Exhibitor",
                                                             domain=[('is_event_related_issue','=',True),
                                                                     ('model','=','sale.order')])
    event_exhibitor_send_quotation_to_exhibitor = fields.Many2one('mail.template',string="Send Quotation to Exhibitor",
                                                                  domain=[('is_event_related_issue','=',True),
                                                                          ('model','=','sale.order')])
    event_exhibitor_already_registered_visitor = fields.Many2one('mail.template',string="Already Registered Visitor Mail",
                                                                 domain=[('is_event_related_issue','=',True),
                                                                         ('model','=','event.registration')])



class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_event_related_issue = fields.Boolean(string='Is Event Related Issue',default=False)