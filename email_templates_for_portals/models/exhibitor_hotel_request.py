from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ExhibitorInvitationLetterRequest(models.Model):
    _inherit = 'exhibitor.invitation.letter.request'

    def action_sent_invitation(self):
        mail_template = self.env.ref('email_templates_for_portals.email_template_invite_letter')
        mail_template.send_mail(self.id, force_send=True)
    @api.model_create_multi
    def create(self, vals_list):
        res = super(ExhibitorInvitationLetterRequest, self).create(vals_list)
        for invitation_letter in res:
                invitation_letter.action_sent_invitation()
        return res




class ExhibitorHotelRequest(models.Model):
    _inherit = 'exhibitor.hotel.request'
    def approve_hotel_request(self):
        res = super().approve_hotel_request()
        print(self.file_name)
        mail_template = self.env.ref('email_templates_for_portals.email_template_exhibitor_hotel_request')
        attachment_id  = self.env['ir.attachment'].sudo().create({
                            'name': self.file_name,
                            'datas': self.upload_voucher,
                            'type': 'binary',
                            'public': True
                        })
        mail_template.attachment_ids = [attachment_id.id]
        mail_template.send_mail(self.id, force_send=True)
        return res
    
class BoothDesignLine(models.Model):
    _inherit = 'booth.design.line'

    def write(self, vals):
        res = super(BoothDesignLine, self).write(vals)
        return res
    
    
    
# class ExhibitorContract(models.Model):
#     _inherit = 'exhibitor.contract'
#
#     is_sent_notification_exhibitor_floor_plan = fields.Boolean(default=False)
#     is_sent_submission_mail = fields.Boolean(default=False)






