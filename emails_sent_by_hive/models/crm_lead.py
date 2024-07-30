from datetime import datetime, timedelta

from odoo import models
from odoo.tools import populate
from odoo.addons.crm.populate import tools


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def send_exhibitor_registration_mail_to_planner(self):
        user = self.env.ref('base.user_admin')
        if self.event_id:
            mail_template = self.event_id.exhibitor_registeration_template
        else:
            mail_template = self.env.ref(
                'techfuge_customisation.email_template_exhibitor_registration_mail_to_planner')
        mail_template.sudo().with_user(user.id).send_mail(self.id, force_send=True)

        # mail_template = self.event_id.event_exhibitor_mail_to_planner
        # mail_template.sudo().with_user(user.id).send_mail(self.id, force_send=True)

    def send_exhibitor_registration_mail_to_exhibitor(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'techfuge_customisation.email_template_exhibitor_registration_mail_to_exhibitor')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        res = super().action_invoice_sent()
        mail_template = self.event_id.event_exhibitor_send_invoice_to_exhibitor
        res['context']['default_template_id'] = mail_template.id
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    def action_quotation_send(self):
        res = super().action_quotation_send()
        if self.env.context.get('proforma'):
            mail_template = self.event_id.event_exhibitor_pro_forma_to_exhibitor
        else:
            mail_template = self.event_id.event_exhibitor_send_quotation_to_exhibitor
            if self.opportunity_id:
                self.opportunity_id.stage_id = self.env.ref('crm.stage_lead3').id
        res['context']['default_template_id'] = mail_template.id
        return res
class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def action_send_visitor_badge_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.event_id.event_exhibitor_already_registered_visitor
        for attendee in self.filtered(
                lambda att: att.source_of_registration in ('onsite_registration', 'excel_upload')):
            if not attendee.badge_sent:
                mail_template.with_user(user.id).sudo().send_mail(attendee.id, force_send=True)
                attendee.badge_sent = True
                attendee.get_badge_attachment()