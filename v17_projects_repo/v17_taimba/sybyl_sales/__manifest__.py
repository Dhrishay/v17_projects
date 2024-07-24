# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
{
    'name': "Sybyl Sales",
    'version': '17.0.0.1',
    'author': "Sybyl Cloud",
    'website': "www.sybylcloud.com, www.sybyl.com",
    'category': 'Sales',
    'summary': 'Sales Operations',
    'description': """
        Dashbord Report Work with Routes.
        Cancel Quotation after Expire
        Check Stock Availability on Quote Confirmation.
        Add Quantity from Sale shop in Floating Form
        Add Route in Billing Address
    """,
    'depends': ['sale_management', 'stock', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/cancel_quotation_cron.xml',
        'data/crm_tags.xml',
        'views/res_config_settings_views.xml',
        'views/sale_shop.xml',
    ],
    'demo': [
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'sybyl_sales/static/src/js/customer_address.js',
    #         'sybyl_sales/static/src/js/update_price.js',
    #     ],
    # },
    'license': 'AGPL-3',
}
