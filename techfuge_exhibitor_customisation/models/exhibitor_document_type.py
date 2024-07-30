# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ExhibitorDocumentType(models.Model):
    _name = 'exhibitor.document.type'
    _description = 'Exhibitor Document Type'

    name = fields.Char(string='Name',store=True)
    document_format = fields.Selection([
        ('pdf', 'PDF'), ('mp4', 'MP4'), ('jpeg', 'JPEG')],
        string="Format")
    document_size = fields.Integer(string="Size")
    document_applicable_ids = fields.Many2many('exhibitor.document.applicable', string="Applicable in")
    document_mandatory_ids = fields.Many2many('exhibitor.document.mandatory', string="Mandatory in")
    document_note = fields.Text(string="Note")




    @api.model
    def get_document_information(self, type_id):
        document_data = {}
        if type_id:
            document_type = self.sudo().browse(int(type_id))
            if document_type:
                document_data.update({
                    'document_size': document_type.document_size,
                    'document_format': document_type.document_format,
                    'document_note': document_type.document_note
                })
        return document_data


class ExhibitorDocumentApplicable(models.Model):
    _name = 'exhibitor.document.applicable'
    _description = 'Exhibitor Document Applicable'

    name = fields.Char(string='Name')


class ExhibitorDocumentMandatory(models.Model):
    _name = 'exhibitor.document.mandatory'
    _description = 'Exhibitor Document Mandatory'

    name = fields.Char(string='Name')
