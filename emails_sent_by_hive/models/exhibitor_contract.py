from odoo import api, fields, models, _

class ExhibitorContract(models.Model):
    _inherit = 'exhibitor.contract'



    def grant_portal_access_to_exhibitor(self):
        for contract in self.filtered(lambda c: c.dashboard_access == 'pending'):
            if contract.sale_order_id.opportunity_id:
                if contract.sale_order_id.opportunity_id.stage_id.is_won:
                    if not contract.exhibitor_user_id:
                        exhibitor_user = contract.sale_order_id.create_portal_user_for_exhibitor()
                        if exhibitor_user:
                            contract.exhibitor_user_id = exhibitor_user.id
                            exhibitor_user.hall_ids = contract.sale_order_id.hall_ids.ids
                            stand_ids = []
                            for stand in contract.sale_order_id.stand_ids:
                                if stand.stand_id.id not in stand_ids:
                                    stand_ids.append(stand.stand_id.id)
                            exhibitor_user.stand_ids = stand_ids
                            self.exhibitor_user_id = exhibitor_user.id
                            user = self.env.ref('base.user_admin')
                            if contract.sale_order_id.opportunity_id:
                                lead_id = contract.sale_order_id.opportunity_id
                                if  self.event_id.event_exhibitor_confirmation:
                                    mail_template = self.event_id.event_exhibitor_confirmation
                                    mail_template.with_user(user.id).sudo().with_context(
                                        partner_full_name=contract.partner_id.name).send_mail(lead_id.id, force_send=True)