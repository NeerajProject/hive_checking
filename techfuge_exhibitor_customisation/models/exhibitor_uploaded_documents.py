# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ExhibitorUploadedDocuments(models.Model):
    _name = 'exhibitor.uploaded.documents'
    _description = 'Exhibitor Uploaded Documents'

    exhibitor_contract_id = fields.Many2one("exhibitor.contract", string="Exhibitor Contract")
    exhibitor_name = fields.Char(string="Exhibitor Name", related="exhibitor_contract_id.exhibitor_name")
    contractor_details_id = fields.Many2one("exhibitor.contractor.details", string="Contractor Details")
    event_id = fields.Many2one("event.event", string="Event")
    hotel_request_id = fields.Many2one("exhibitor.hotel.request", string="Hotel Request")
    document_type_id = fields.Many2one("exhibitor.document.type", string="Document Type")
    document_note = fields.Text(string="Note")
    document_attachment_id = fields.Many2one('ir.attachment', string="Uploaded Document Attachment")
    company_name = fields.Char(related='exhibitor_contract_id.company_name',store=True)

    def download_other_uploaded_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.document_attachment_id.id,
            'target': 'self',
        }
