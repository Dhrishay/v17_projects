# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2019 Skyscend Business Solutions (<http://skyscendbs.com>)

{
    'name': 'Taimba - Partners',
    'category': 'other',
    'version': '17.0.0.1',
    'license': 'AGPL-3',
    'description': """
Taimba partners.
Is customer , Is supplier flag
Phone number and name mandatory for customers only
=======================================================
Partners
    """,
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'depends': ['base','account'],
    'data': [
        'views/partner_view.xml'
        ],
    'installable': True,
}
