# -*- encoding: utf-8 -*-
##########################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions Pvt. Ltd. (https://www.skyscendbs.com)
#
##########################################################################################
{
    'name': 'Sale Customer',
    'version': '17.0',
    'category': 'Sale',
    'license': 'AGPL-3',
    'summary': 'Display only customers in sale orders.',
    'description': """
    This module allows to filter the partners such that only customers will be displayed on sales order.
    """,
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'https://www.skyscendbs.com',
    'depends': ['sky_account_customer_supplier', 'sale_management'],
    'images': ['static/description/images/customer_sale_image.png'],
    'installable': True,
    'auto_install': False
}
