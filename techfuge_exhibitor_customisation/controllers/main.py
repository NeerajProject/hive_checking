# -*- coding: utf-8 -*-

import logging

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import ast

_logger = logging.getLogger(__name__)


class Binary(http.Controller):

    @http.route('/web/binary/download_multiple_attachments', type='http', auth="public")
    def download_multiple_attachments(self, attachments, res_model=False, res_id=False, **kw):
        print('download_multiple_attachments',attachments)
        attachment_list = ast.literal_eval(attachments)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', attachment_list)])
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                file_name = attachment_id.name
                file_path = attachment_id._full_path(file_store)
                file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
        zip_filename = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        if res_model and res_id:
            record = request.env[res_model].sudo().browse(int(res_id))
            if record:
                zip_filename = record.company_name + ' - ' + str(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

        zip_filename = "%s.zip" % zip_filename
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
        for file_info in file_dict.values():
            zip_file.write(file_info["path"], file_info["name"])
        zip_file.close()
        print("issue")
        return request.make_response(
            bitIO.getvalue(), headers=[
                ('Content-Type', 'application/x-zip-compressed'),
                ('Content-Disposition', content_disposition(zip_filename))
            ]
        )
