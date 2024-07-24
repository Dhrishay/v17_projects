# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
{
    'name': 'Create Loading Unloading Mechanism',
    'summary': 'Loading and Unloading Order in Warehouse',
    'category': '',
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'http://www.skyscendbs.com',
    'license': 'AGPL-3',
    'version': '17.0.0.0',
    'depends': [
        'base',
        'sale',
        'sale_management',
        'fleet',
        'sky_route',
        'sky_base_user',
        'sky_base_api',
        # 'sky_sale_stock_custom'
    ],
    'data': [
        'security/ir.model.access.csv',
             'data/sequence.xml',
             'views/loading.xml',
             'views/unloading.xml',
             'views/driver_res_partner.xml',
             'views/vehicle_sale_order.xml',
             'views/shipment_driver.xml',
             'views/warehouse_vehicle.xml',
             'views/driver_account_move.xml',
             'views/account_payment_view.xml',
             'views/sky_fleet.xml',
             ],
    # 'demo': ['Demo'],

    'installable': True,
    'application': True,
    'auto_install': False
}
