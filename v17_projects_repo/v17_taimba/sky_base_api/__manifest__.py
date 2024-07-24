# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
{
    'name': 'Auth Token',
    'summary': 'Login into Odoo with token',
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'http://www.skyscendbs.com',
    'license': 'AGPL-3',
    'category': 'Tools',
    'version': '17.0.0.1',
    'depends': [
        'base',
        'portal',
        'web',
        'sky_base_user',
        'sky_route',
        'partner_firstname',
    ],
    'data': [
        "security/ir.model.access.csv",
        "data/ir_config_param.xml",
        'views/res_users_views.xml',

    ],
}
