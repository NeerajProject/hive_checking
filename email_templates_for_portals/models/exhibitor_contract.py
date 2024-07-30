from odoo import fields, models, api


class ExhibitorHotelRequest(models.Model):
    _inherit = 'exhibitor.hotel.request'



    @api.model_create_multi
    def create(self, vals_list):
        print(">>>>>>> hotel booking")
        is_portal = self.env.user.has_group('base.group_portal')
        res = super(ExhibitorHotelRequest, self).create(vals_list)
        if is_portal:
            res.exhibitor_contract_id.sent_notification_to_hotel_request_hive()
        return  res

class ContractorUploadedDocuments(models.Model):
    _inherit = 'contractor.uploaded.documents'

    not_is_contractor_documents_sent = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        is_portal = self.env.user.has_group('base.group_portal')
        if is_portal:
            res = super(ContractorUploadedDocuments, self).create(vals_list)
            res.not_is_contractor_documents_sent = True
            res.contractor_id.exhibitor_contract_id.is_contractor_document_sent=True

            return res
        else:
            return super(ShipmentUploadedDocuments, self).create(vals_list)

class ExhibitorContractorDetails(models.Model):
    _inherit = 'exhibitor.contractor.details'
    @api.model_create_multi
    def create(self, vals_list):
        print(">>>>>>>>>>> yessssssssssssssss")
        is_portal = self.env.user.has_group('base.group_portal')
        res = super(ExhibitorContractorDetails, self).create(vals_list)
        print(res)
        res.exhibitor_contract_id.sent_contractor_notification_mail_mail()
        return res


class ShipmentUploadedDocuments(models.Model):
    _inherit = 'shipment.uploaded.documents'
    is_shipping_mail_sent = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        is_portal = self.env.user.has_group('base.group_portal')
        if is_portal:
            res = super(ShipmentUploadedDocuments, self).create(vals_list)
            res.is_shipping_mail_sent = True

            res.exhibitor_contract_id.is_shipping_mail_sent = True
            return res
        else:
            return super(ShipmentUploadedDocuments, self).create(vals_list)



class ExhibitorContract(models.Model):
    _inherit = 'exhibitor.contract'

    is_exihibitor_sent_stand_info = fields.Boolean(default=False)
    is_omg_sent_stand_info = fields.Boolean(default= False)
    is_submission_mail_sent = fields.Boolean(default= False)
    is_shipping_mail_sent = fields.Boolean(default=False)
    is_contractor_document_sent = fields.Boolean(default=False)
    is_notification_of_contractor_create = fields.Boolean(default=False)



    def write(self, vals):
        if self:
            self.clear_caches()
        print(">>>>>>>>>",vals)
        res = super().write(vals)

        if  'is_exihibitor_sent_stand_info' in vals.keys() :
            if vals['is_exihibitor_sent_stand_info']:
                pass
            else:
                self.is_exihibitor_sent_stand_info = True
                for rec in self.floor_plan_ids.filtered(lambda status: status.status =='submitted'):
                    rec.sent_stand_info_to_exhibitor()
                    break
                return res
        else:
            return  res







    def sent_notification_to_hotel_request_hive(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_exhibitor_hotel_notification')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)

    # def write(self, vals):
    #     is_portal = self.env.user.has_group('base.group_portal')
    #     res =  super(ExhibitorContract, self).write(vals)
    #     print( 'def write(self, vals):',res)
    #     # if is_portal:
    #     #     res.is_submission_mail_sent = True
    #     return res


    def sent_contractor_notification_mail_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_contractor_contractor_portal_waring_exhibitors')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)


    def sent_contractor_documents_mail_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_contractor_documents_exhibitors')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)

    def sent_shipping_mail_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_shipment_specification')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)

    def sent_submission_info_mail(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_submission_of_email')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)


    def is_sent_notification_exhibitor_floor_plans(self):
        contractor =  self.env['exhibitor.contract'].search([])
        for rec in contractor:

            # if rec.is_exihibitor_sent_stand_info:
            #     try:
            #         rec.sent_stand_info_to_exhibitor()
            #         rec.is_exihibitor_sent_stand_info = False
            #         for records in rec.floor_plan_ids:
            #             records.is_exihibitor_sent_stand_info = False
            #     except:
            #         pass

            if rec.is_submission_mail_sent:
                try:
                    rec.sent_submission_info_mail()
                    rec.is_submission_mail_sent = False
                except Exception:
                    pass

            if rec.is_contractor_document_sent:
                try:
                    rec.sent_contractor_documents_mail_mail()
                    rec.is_contractor_document_sent = False
                    for records in rec.contractor_document_ids:
                        records.not_is_contractor_documents_sent = False

                except:
                    pass

            # if rec.is_omg_sent_stand_info:
            #     rec.sent_stand_info_to_hive()
            #     rec.is_omg_sent_stand_info = False
            #     for records in rec.floor_plan_ids:
            #         records.is_omg_sent_stand_info = False

            if rec.is_shipping_mail_sent:
                try:
                    rec.sent_shipping_mail_mail()
                    rec.is_shipping_mail_sent = False
                    for records in rec.shipment_document_ids:
                        records.is_shipping_mail_sent = False
                except:
                    pass
            # if rec.is_notification_of_contractor_create:
            #     rec.sent_contractor_notification_mail_mail()
            #     rec.is_notification_of_contractor_create = False

class ExhibitorContract(models.Model):
    _inherit = 'booth.design.line'
    is_exihibitor_sent_stand_info = fields.Boolean(default=False)
    is_omg_sent_stand_info = fields.Boolean(default= False)



    def sent_stand_info_to_exhibitor(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_booth_design_line_exhibitor_upload')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)
    def sent_stand_info_to_hive(self):
        user = self.env.ref('base.user_admin')
        mail_template = self.env.ref(
            'email_templates_for_portals.email_template_booth_design_line_exhibitor')
        mail_template.with_user(user.id).sudo().send_mail(self.id, force_send=True)

    @api.model_create_multi
    def create(self, vals_list):
       print("create portal")
       is_portal = self.env.user.has_group('base.group_portal')
       if is_portal:
            # vals_list['is_omg_sent_stand_info'] = True
            res = super(ExhibitorContract, self).create(vals_list)
            # res.sent_stand_info_to_hive()
            return res



       else:
           # vals_list['is_exihibitor_sent_stand_info'] = True
           res = super(ExhibitorContract, self).create(vals_list)
           # res.sent_stand_info_to_exhibitor()
           res.is_exihibitor_sent_stand_info = False
           res.exhibitor_contract_id.is_exihibitor_sent_stand_info = False
           return res



