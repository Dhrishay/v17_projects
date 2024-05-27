{
    'name': 'Stock Cleaning',
    'version': '17.0.1.1.1',
    'category': 'Inventory',
    'license': 'OPL-1',
    'description': """
    This module is used for Stock Cleaning from location.
    """,
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'http://www.skyscendbs.com',
    'depends': ['mrp', 'stock', 'sale_management', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_location_clean_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

