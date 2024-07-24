# -*- encoding: utf-8 -*-
##########################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions Pvt. Ltd. (https://www.skyscendbs.com)
#
##########################################################################################
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('ke_taimba')
    def _get_taimba_template_data(self):
        return {
            'name': 'Taimba',
            'property_account_receivable_id': 'taimba_12021',
            'property_account_payable_id': 'taimba_2101030',
            'property_account_expense_categ_id': 'taimba_620104',
            'property_account_income_categ_id': 'taimba_4000',
            'code_digits': '6',
        }

    @template('ke_taimba', 'res.company')
    def _get_taimba_ke_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.ke',
                'currency_id': 'base.KES',
                'bank_account_code_prefix': '120',
                'cash_account_code_prefix': '120',
                'transfer_account_code_prefix': '120',
                'income_currency_exchange_account_id': 'cash_diff_income',
                'expense_currency_exchange_account_id': 'cash_diff_expense',
            },
        }
