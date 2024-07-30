# -*- coding: utf-8 -*-

from odoo import models, _, fields
from odoo.tools.misc import format_date


class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'
    _description = 'Partner Ledger in Transaction Currency'

    def _get_report_line_partners(self, options, partner, partner_values, level_shift=0):
        context = self.env.context
        if 'in_transaction_currency' in context and context['in_transaction_currency']:
            company_currency = self.env.company.currency_id
            unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')

            unfoldable = False
            column_values = []
            report = self.env['account.report']
            for column in options['columns']:
                col_expr_label = column['expression_label']
                value = partner_values[column['column_group_key']].get(col_expr_label)
                txn_currency = self.env['res.currency'].search([('name', '=', 'USD')])
                value_in_txn_currency = None
                if value:
                    value_in_txn_currency = company_currency._convert(
                        value,
                        txn_currency,
                        self.env.company,
                        fields.Date.today()
                    )

                if col_expr_label in {'debit', 'credit', 'balance'}:
                    formatted_value = report.format_value(
                        value_in_txn_currency,
                        currency=txn_currency,
                        figure_type=column['figure_type'],
                        blank_if_zero=column['blank_if_zero']
                    )
                else:
                    formatted_value = report.format_value(
                        value, figure_type=column['figure_type']
                    ) if value is not None else value

                unfoldable = unfoldable or (
                        col_expr_label in ('debit', 'credit') and not company_currency.is_zero(value)
                )

                column_values.append({
                    'name': formatted_value,
                    'no_format': value,
                    'class': 'number'
                })

            line_id = report._get_generic_line_id('res.partner',
                                                  partner.id) if partner else report._get_generic_line_id(None, None,
                                                                                                          markup='no_partner')

            return {
                'id': line_id,
                'name': partner is not None and (partner.name or '')[:128] or _('Unknown Partner'),
                'columns': column_values,
                'level': 2 + level_shift,
                'trust': partner.trust if partner else None,
                'unfoldable': unfoldable,
                'unfolded': line_id in options['unfolded_lines'] or unfold_all,
                'expand_function': '_report_expand_unfoldable_line_partner_ledger',
            }

        else:
            return super()._get_report_line_partners(options, partner, partner_values, level_shift)

    def _get_report_line_move_line(self, options, aml_query_result, partner_line_id, init_bal_by_col_group,
                                   level_shift=0):
        context = self.env.context
        if 'in_transaction_currency' in context and context['in_transaction_currency']:
            company_currency = self.env.company.currency_id

            if aml_query_result['payment_id']:
                caret_type = 'account.payment'
            else:
                caret_type = 'account.move.line'

            columns = []
            report = self.env['account.report']
            for column in options['columns']:
                col_expr_label = column['expression_label']
                if col_expr_label == 'ref':
                    col_value = report._format_aml_name(
                        aml_query_result['name'], aml_query_result['ref'], aml_query_result['move_name']
                    )
                else:
                    col_value = aml_query_result[col_expr_label] if column['column_group_key'] == aml_query_result[
                        'column_group_key'] else None

                if col_value is None:
                    columns.append({})
                else:
                    col_class = 'number'

                    if col_expr_label == 'date_maturity':
                        formatted_value = format_date(self.env, fields.Date.from_string(col_value))
                        col_class = 'date'
                    elif col_expr_label == 'amount_currency':
                        currency = self.env['res.currency'].browse(aml_query_result['currency_id'])
                        formatted_value = report.format_value(
                            col_value, currency=currency, figure_type=column['figure_type']
                        )
                    elif col_expr_label == 'balance':
                        col_value += init_bal_by_col_group[column['column_group_key']]
                        txn_currency = self.env['res.currency'].browse(aml_query_result['currency_id'])
                        value_in_txn_currency = company_currency._convert(
                            col_value,
                            txn_currency,
                            self.env.company,
                            fields.Date.today()
                        )
                        formatted_value = report.format_value(
                            value_in_txn_currency,
                            currency=txn_currency,
                            figure_type=column['figure_type'],
                            blank_if_zero=column['blank_if_zero']
                        )
                    elif col_expr_label in ('debit', 'credit'):
                        txn_currency = self.env['res.currency'].browse(aml_query_result['currency_id'])
                        value_in_txn_currency = company_currency._convert(
                            col_value,
                            txn_currency,
                            self.env.company,
                            fields.Date.today()
                        )
                        formatted_value = report.format_value(
                            value_in_txn_currency,
                            currency=txn_currency,
                            figure_type=column['figure_type'],
                        )
                    else:
                        if col_expr_label == 'ref':
                            col_class = 'o_account_report_line_ellipsis'
                        elif col_expr_label not in ('debit', 'credit'):
                            col_class = ''
                        formatted_value = report.format_value(col_value, figure_type=column['figure_type'])

                    columns.append({
                        'name': formatted_value,
                        'no_format': col_value,
                        'class': col_class,
                    })

            return {
                'id': report._get_generic_line_id('account.move.line', aml_query_result['id'],
                                                  parent_line_id=partner_line_id),
                'parent_id': partner_line_id,
                'name': format_date(self.env, aml_query_result['date']),
                'class': 'text-muted' if aml_query_result['key'] == 'indirectly_linked_aml' else 'text',
                # do not format as date to prevent text centering
                'columns': columns,
                'caret_options': caret_type,
                'level': 2 + level_shift,
            }

        else:
            return super()._get_report_line_move_line(
                options, aml_query_result, partner_line_id, init_bal_by_col_group, level_shift
            )

    def _get_report_line_total(self, options, totals_by_column_group):
        context = self.env.context
        if 'in_transaction_currency' in context and context['in_transaction_currency']:
            company_currency = self.env.company.currency_id
            column_values = []
            report = self.env['account.report']
            for column in options['columns']:
                col_expr_label = column['expression_label']
                value = totals_by_column_group[column['column_group_key']].get(column['expression_label'])
                if col_expr_label in {'debit', 'credit', 'balance'}:
                    txn_currency = self.env['res.currency'].search([('name', '=', 'USD')])
                    value_in_txn_currency = company_currency._convert(
                        value,
                        txn_currency,
                        self.env.company,
                        fields.Date.today()
                    )
                    formatted_value = report.format_value(
                        value_in_txn_currency,
                        currency=txn_currency,
                        figure_type=column['figure_type'],
                        blank_if_zero=False
                    )
                else:
                    formatted_value = report.format_value(value, figure_type=column['figure_type']) if value else None

                column_values.append({
                    'name': formatted_value,
                    'no_format': value,
                    'class': 'number'
                })

            return {
                'id': report._get_generic_line_id(None, None, markup='total'),
                'name': _('Total'),
                'class': 'total',
                'level': 1,
                'columns': column_values,
            }

        else:
            return super()._get_report_line_total(options, totals_by_column_group)
