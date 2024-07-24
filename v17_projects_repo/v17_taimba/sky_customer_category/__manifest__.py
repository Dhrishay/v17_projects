# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################

{
    'name': 'Taimba - Sky customer category',
    'category': 'sale',
    'version': '17.0.0.1',
    'license': 'AGPL-3',
    'description': """
Taimba customer category.
=======================================================
Customers
    """,
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'https://www.skyscendbs.com',
    'depends': ['sale_management', 'product'],
    'data': [
        'views/partner_view.xml',
        'views/product_pricelist_view.xml'
        ],
    'installable': True,
}
