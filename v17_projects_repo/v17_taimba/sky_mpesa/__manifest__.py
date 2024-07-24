# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
{
    'name': 'Sky MPESA',
    'version': '17.0.0.0.1',
    'category': 'other',
    'summary': '',
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'description': "Mpesa ",
    'depends': ['base',
                'sky_base_api',
                'sale_stock',
                'sky_route',
                ],
    'data': ['security/ir.model.access.csv',
             'data/sequence.xml',
             'views/mpesa.xml',
             'views/account_journal_view.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
