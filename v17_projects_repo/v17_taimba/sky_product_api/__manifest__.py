# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
{
    'name': 'Product API',
    'version': '17.0.0.0.1',
    'category': 'other',
    'summary': '',
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'description': "Product API",
    'depends': [
             'base',
             'contacts',
             'base_geolocalize',
             'sky_loading_mechanism',
             'sky_account_customer_supplier',
             'account_followup',
             'sky_mpesa',
            ],
    'data': [
             'data/product_pricelist_data.xml',
             'security/ir.model.access.csv',
             'views/res_partner_type.xml',
             'views/mobile_payment.xml',
             'views/sale_order_status.xml',
             'views/price_list_type.xml',
             'views/customer_type.xml',
             'views/product_template_view.xml',
             'views/product_product_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}

