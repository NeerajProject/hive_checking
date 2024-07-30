# -*- coding: utf-8 -*-

from odoo import api, fields, models,_


class ExhibitorInvitationLetterRequest(models.Model):
    _name = 'exhibitor.invitation.letter.request'
    _description = 'Exhibitor Invitation Letter Request'


    reference_no = fields.Char(string='Order Reference', required=True,
                          readonly=True, default=lambda self: _('New'))
    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_name = fields.Char(string="Exhibitor Name", related="exhibitor_contract_id.exhibitor_name")
    event_id = fields.Many2one("event.event", string="Event")
    attendee_id = fields.Many2one("event.registration", string="Attendee")
    name = fields.Char(string="Attendee Name", related="attendee_id.attendee_full_name")
    passport_number = fields.Char(string="Passport Number")
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    date_of_birth = fields.Date(string="Date of Birth")
    country_id = fields.Many2one("res.country", string="Nationality")
    from_date = fields.Date(string="Travel From Date")
    till_date = fields.Date(string="Travel Till Date")
    no_of_days = fields.Integer(string="No. of Days")
    letter_attachment_id = fields.Many2one('ir.attachment', string="Invitation Letter Attachment")
    invitation_letter_signed = fields.Binary(string="Invitation Letter Signed")
    signed_letter_attachment_id = fields.Many2one('ir.attachment', string="Signed Invitation Letter Attachment")
    status = fields.Selection(selection=[
        ('new', 'New'),
        ('issued', 'Letter Issued')
    ], string="Status", default="new", compute="_compute_letter_request_status")
    invitation_letter_date = fields.Date(compute="_compute_today_date")







    def _compute_today_date(self):
        self.invitation_letter_date = fields.Datetime.today()
    def write(self, vals):
        if 'invitation_letter_signed' in vals:
            signed_letter_attachment = self.env['ir.attachment'].sudo().create({
                'name': 'Invitation Letter - %s.pdf' % self.name,
                'datas': vals['invitation_letter_signed'],
                'type': 'binary',
                'public': True
            })
            vals['signed_letter_attachment_id'] = signed_letter_attachment.id
        return super().write(vals)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'exhibitor.invitation.letter.request') or _('New')
        res = super(ExhibitorInvitationLetterRequest, self).create(vals)
        return res
    def download_invitation_letter_attachment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.letter_attachment_id.id,
            'target': 'self',
        }

    @api.depends('signed_letter_attachment_id')
    def _compute_letter_request_status(self):
        for request in self:
            request.status = "new"
            if request.signed_letter_attachment_id:
                request.status = "issued"
