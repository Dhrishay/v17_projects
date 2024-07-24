# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2019 Skyscend Business Solutions (<http://skyscendbs.com>)

{
    'name': 'Taimba - Sky Customer Supplier Account ',
    'category': 'other',
    'version': '17.0.0.1',
    'license': 'AGPL-3',
    'description': """
Taimba Customers Customer Invoices and payments
and Suppliers on Vendor bills and payments.
=======================================================
Partners
    """,
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'depends': ['account','sky_customer_supplier'],
    'data': ['views/view_move_form.xml'],
    'installable': True,
}
