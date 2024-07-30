# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ContractorUploadedDocuments(models.Model):
    _name = 'contractor.uploaded.documents'
    _description = 'Contractor Uploaded Documents'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    event_id = fields.Many2one("event.event", string="Event")
    document_type_id = fields.Many2one("exhibitor.document.type", string="Document Type")
    document_note = fields.Text(string="Note")
    document_attachment_id = fields.Many2one('ir.attachment', string="Uploaded Document Attachment")
    contractor_id = fields.Many2one('exhibitor.contractor.details',string="Contractor")
    contractor_contractor_full_name = fields.Char(related="contractor_id.contractor_full_name")
    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submitted', 'Submit'),
        ('confirm', 'Confirm')
    ], string='Status', default='draft')
    def download_contractor_uploaded_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.document_attachment_id.id,
            'target': 'self',
        }
