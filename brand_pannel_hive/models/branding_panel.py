from odoo import api, fields, models, tools, _, Command
from odoo.exceptions import MissingError, ValidationError, AccessError
from odoo.exceptions import ValidationError
import json


class ResCountryCodeMaster(models.Model):
    _name = 'res.country.code.master'
    _rec_name = 'code'
    code =  fields.Char(string='Code')
    country = fields.Char(string="Country")

class MailMessage(models.Model):
    _inherit='mail.message'

    # @api.model
    # def create(self, vals):
    #     # your logic
    #
    #     print(vals)
    #
    #     user=self.env.user
    #
    #     if user.user_has_groups('base.group_portal'):
    #         if vals['model'] == 'booth.design.line':
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #             contract = self.env['exhibitor.contract'].sudo().search([
    #                 ('partner_id', '=', +self.env.user.partner_id.id)
    #             ], limit=1)
    #             self.env['mail.activity'].sudo().create(
    #
    #
    #                 {'res_name': "You have a message",
    #                  'company_name' : contract.company_name,
    #                  'section': 'Floor Planning',
    #                  'activity_type_id': self.env.ref('brand_pannel_hive.portal_users_activity').id,
    #                  'res_name':  'You have a Floor Plan  Suggestion from '+self.env.user.partner_id.name,
    #                  'note': vals['body'],
    #                  'summary': 'You have a Floor Plan  Suggestion from '+self.env.user.partner_id.name,
    #                  'user_id': user.id,
    #                  'res_model_id': self.env.ref('brand_pannel_hive.model_booth_design_line').id,
    #                  'res_id': vals['res_id']
    #                  })
    #
    #     rec = super(MailMessage, self).create(vals)
    #
    #     # your logic
    #
    #     return rec

class BoothDesign(models.Model):
    _name = 'booth.design.type'
    name = fields.Char(String="Name")

    @api.constrains('name')
    def _check_name(self):
        _document_name = self.env['booth.design.type'].sudo().search(
            [('id', '!=', self.id), ('name', '=', self.name)])
        if _document_name:
            raise ValidationError(_(" Name must be Unique, already this name exists!"))



class BoothDesignLine(models.Model):
    _name = 'booth.design.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'stand_name'


    stand_id = fields.Many2one('exhibitor.stand.details')
    description = fields.Char()
    stand_name = fields.Char(related='stand_id.stand_number',store=True)
    partner_id = fields.Many2one('res.partner',related="exhibitor_contract_id.partner_id")
    exhibitor_contract_id = fields.Many2one('exhibitor.contract',string="Exhibitor")
    booth_design_id = fields.Many2one('booth.design.type',string=" Type")
    attachement_ids = fields.Many2many('ir.attachment', tracking=True,attachment=True)
    exhibitor_upload = fields.Many2one( 'ir.attachment',tracking=True,attachment=True)
    is_latest = fields.Boolean()
    event_id = fields.Many2one(related="exhibitor_contract_id.event_id")

    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submitted','Send'),
        ('accepted', 'Accepted'),
        ('cancel','Cancel'),
        ('decline','Decline')
    ], string='Status',default='draft')
    date_of_upload = fields.Date(string='DATE',default=fields.datetime.now())


    by_iff_exihibitor = fields.Selection([
        ('omg', 'OMG'),
        ('exhibitor', 'Exhibitor')
    ],default='omg')

    stand_id_domain = fields.Char(
        compute="_compute_stand_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends('stand_id','exhibitor_contract_id')
    def _compute_stand_id_domain(self):
        for rec in self:
            domain =[]
            for stand in rec.exhibitor_contract_id.stand_ids:
                    domain.append(stand.stand_id.id)
            rec.stand_id_domain = json.dumps([('id', 'in', domain)])



    @api.model_create_multi
    def create(self,values):
        record = super(BoothDesignLine, self).create(values)
        return record


    def get_download_exhibitor_upload(self):
        for rec in self.exhibitor_upload:
            documents = []
            for rec in self.exhibitor_upload:
                rec.public = True
                url = '/web/content/' + str(rec.id) + "?download=true"
                documents.append([rec.name, url])
            return documents


    def download_floor_client_plan_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % self.exhibitor_upload.id,
            'target': 'self',
        }



    def write(self, vals):
        res = super().write(vals)
        print(vals)
        if 'attachement_ids' in vals:
            self.message_post(body="Previous Floor Plan",      message_type='comment',
                    subtype_xmlid='mail.mt_comment',attachment_ids=self.attachement_ids.ids)
        return res












    def generate_download_url(self):
        documents = []
        for rec in self.attachement_ids:
            rec.public=True
            url ='/web/content/'+str(rec.id)+"?download=true"
            documents.append([rec.name,url])
        return documents






class BrandingUpdateLine(models.Model):
    _name = 'branding.update.line'
    partner_id = fields.Many2one("res.partner",related="exhibitor_contract_id.partner_id")
    stand_id = fields.Many2one('exhibitor.stand.details',string="Stand Details")
    event_id =  fields.Many2one(related="exhibitor_contract_id.event_id",stored=True)
    exhibitor_contract_id = fields.Many2one('exhibitor.contract',string="Exhibitor")
    category_accessories = fields.Many2many('accessories.branding.type',related="exhibitor_contract_id.category_accessories")
    category_furniture = fields.Many2many('furniture.branding.type',related="exhibitor_contract_id.category_furniture")
    is_submited = fields.Boolean(related="exhibitor_contract_id.is_submited_branding_panel",string="Submited")

    def _check_already_exist(self,stand_id,event_id):
        return self.search_count([('stand_id','=',int(stand_id)),('event_id','=',int(event_id))])

    def _check_already_update_exist(self,stand_id):
        return self.search_count([('stand_id','=',stand_id),('event_id','=',self.exhibitor_contract_id.event_id.id)])

class BrandingType(models.Model):
    _name = 'accessories.branding.type'

    name = fields.Char(string="Name",required=True)
    sequence = fields.Integer()
    is_others = fields.Boolean(default=False)

    def check_checked(self,ids):
       return self.id in ids


class BrandingType(models.Model):
    _name = 'furniture.branding.type'

    name = fields.Char(string="Name",required=True)
    sequence = fields.Integer()
    is_others = fields.Boolean(default=False)


    def check_checked(self,ids):

       return self.id in ids
class ExhibitorContract(models.Model):
    _inherit = 'exhibitor.contract'

    category_accessories = fields.Many2many('accessories.branding.type')
    category_furniture = fields.Many2many('furniture.branding.type')
    company_logo =  fields.Image()
    contact_details_ids = fields.One2many('res.partner','exhibitor_contract_id')

    floor_plan_ids = fields.One2many('booth.design.line','exhibitor_contract_id')
    is_accepted_floorplan = fields.Boolean(string="Accepted Floor Plan",default = False)
    brand_panel_ids = fields.One2many('branding.update.line','exhibitor_contract_id')
    stand_counts = fields.Integer(default=1)
    is_submited_branding_panel = fields.Boolean(default=False,string='Submited Branding Info')
    branding_panel_company_name = fields.Char(string="Branding Panel Company")
    stand_details_report = fields.Char(compute="compute_stand_details_report" ,store=True)
    is_other_furniture = fields.Char()
    is_other_accessory = fields.Char()

    count_floor_plan = fields.Integer(compute="_compute_floor_plan")

    is_lock_branding_panel = fields.Boolean(default=False)

    branding_panel_width = fields.Float( default=1.22)
    branding_panel_height = fields.Float( default=2.70)

    branding_panel_status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submitted','Submit'),
        ('confirm','Confirm')
    ], string='Branding Status',default='draft')


    def get_country_branding_panel_badge(self):
       country_badge_id = self.event_id.branding_panel_background_id.filtered(lambda rec: rec.country_id.id == self.partner_id.country_id.id)
       if  country_badge_id:
            print("yes")
            pass
       else:
           print("NO")
           country_badge_id = self.event_id.branding_panel_background_id.filtered(
               lambda rec: rec.country_id.id == False)

       return country_badge_id.id


    @api.depends('stand_ids')
    def compute_stand_details_report(self):
        for rec in self:
            stand_report = ""
            for stand  in rec.stand_ids:
                if stand.stand_id:
                    stand_report=stand_report+stand.stand_id.stand_number+"    "
            rec.stand_details_report = stand_report





    def get_succefully_accepted(self):
        print( self.floor_plan_ids)
        for rec in self.floor_plan_ids:
            print(rec.status)
            if rec.status  == 'accepted':
                return True
        return False
    def action_lock_branding_panel(self):
        self.is_lock_branding_panel = True
    def action_unlock_branding_panel(self):
        self.is_lock_branding_panel = False

    def _compute_stand_details(self):
        stands =''
        for rec in self.stand_ids:
            stands=stands+" "+rec.stand_id.stand_number+" ,"
        return stands[:-1]

    @api.depends('floor_plan_ids')
    def _compute_floor_plan(self):
        for rec in self:
            rec.count_floor_plan =   len(rec.floor_plan_ids)


    def action_view_stands_details(self):
            print("sbd")
            self.ensure_one()
            #
            action = {
                'name': "Invoices",
                'type': 'ir.actions.act_window',
                'res_model': 'booth.design.line',
                'target': 'current',
            }
            action['view_mode'] = 'tree,form'
            action['domain'] = [('exhibitor_contract_id', '=', self.id)]
            return action

    def check_count_is_okay(self):
        return len(self.brand_panel_ids.mapped('id'))<self.stand_counts
    def download_documents(self):

        list_of_files = []
        for rec in self.floor_plan_ids:
            list_of_files.append([rec.name,'/web/content/%s?download=true' % rec.id])
        return list_of_files

    def check_stand_already_taken(self,stand_id):
        print("check_stand_already_taken",stand_id)
        return False