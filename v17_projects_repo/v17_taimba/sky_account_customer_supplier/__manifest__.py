# -*- encoding: utf-8 -*-
##########################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions Pvt. Ltd. (https://www.skyscendbs.com)
#
##########################################################################################
{
    'name': 'Account Customer Supplier',
    'version': '17.0',
    'category': 'account',
    'summary': 'A module used to filter customer and supplier on invoice and bills.',
    'description': 'A module used to filter customer and supplier on invoice and bills.',
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'https://www.skyscendbs.com',
    'depends': ['account'],
    'data': [
        'views/res_partner.xml',
        'views/account.xml',
    ],
    'installable': False,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
