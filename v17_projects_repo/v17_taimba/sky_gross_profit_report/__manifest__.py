# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2019 Skyscend Business Solutions (<http://skyscendbs.com>)

{
    'name': 'Taimba - Gross Profict report',
    'category': 'account',
    'version': '17.0.0.1',
    'license': 'AGPL-3',
    'description': """
Gross profit report by product and customer.
=======================================================
Sales
    """,
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'depends': ['sale_margin'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_gpm_by_customer_view.xml',
        'views/report_gpm_by_product_view.xml'
        ],
    'installable': True,
}
