# -*- coding: utf-8 -*-

from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class GeneratePaymentStageWizard(models.TransientModel):
    _name = 'generate.payment.stage.wizard'
    _description = "Generate Payment Stage Wizard"

    no_of_stages = fields.Integer(string="No. of Stages", required=True)

    def generate_payment_stages(self):
        if self.no_of_stages:
            sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))

            if sale_order:
                if sale_order.is_new_payment_template():
                    if sale_order.exhibitor_payment_stage_ids:
                        sale_order.exhibitor_payment_stage_ids.unlink()

                    for stage in range(1, self.no_of_stages + 1):
                        if stage == 1:
                            stage_description = str(stage) + 'st'
                            due_date_days = stage * 10
                        elif stage == 2:
                            if stage == 1:
                                stage_description = str(stage) + 'nd'
                            else:
                                stage_description= "Balance "

                            due_date_days = stage * 10
                        elif stage == 3:
                            if stage == 1:
                                stage_description = str(stage) + 'nd'
                            else:
                                stage_description= "Balance "
                            due_date_days = stage * 10
                        else:
                            stage_description = str(stage) + 'th'
                            due_date_days = stage * 10

                        payment_description = stage_description + ' payment @'+sale_order.currency_id.name
                        paid_percentage = 100 / self.no_of_stages
                        payment_due_date = fields.Date.today() + relativedelta(days=due_date_days)

                        payment_satges=self.env['exhibitor.payment.stages'].create({
                            'sale_order_id': sale_order.id,
                            'name': payment_description,
                            'payment_type': 'percentage',
                            'paid_percentage': paid_percentage,
                            'payment_due_date': payment_due_date,
                        })
                        payment_satges.name = payment_satges.name+"  "+str(payment_satges.paid_amount)+"/ "+sale_order.currency_id.name+" "+str(sale_order.amount_total)+" : ON OF BEFORE "



                else:
                    if sale_order.exhibitor_payment_stage_ids:
                        sale_order.exhibitor_payment_stage_ids.unlink()

                    for stage in range(1, self.no_of_stages + 1):
                        if stage == 1:
                            stage_description = str(stage) + 'ST'
                            due_date_days = stage * 10
                        elif stage == 2:
                            stage_description = str(stage) + 'ND'
                            due_date_days = stage * 10
                        elif stage == 3:
                            stage_description = str(stage) + 'RD'
                            due_date_days = stage * 10
                        else:
                            stage_description = str(stage) + 'TH'
                            due_date_days = stage * 10

                        payment_description = stage_description + ' PAYMENT ON OR BEFORE'
                        paid_percentage = 100 / self.no_of_stages
                        payment_due_date = fields.Date.today() + relativedelta(days=due_date_days)

                        self.env['exhibitor.payment.stages'].create({
                            'sale_order_id': sale_order.id,
                            'name': payment_description,
                            'payment_type': 'percentage',
                            'paid_percentage': paid_percentage,
                            'payment_due_date': payment_due_date,
                        })







