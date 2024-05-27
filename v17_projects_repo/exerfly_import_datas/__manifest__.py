{
    'name': 'Manufacturing BOM',
    'version': '17.0.1.1.1',
    'category': 'Manufacturing/Manufacturing',
    'license': 'OPL-1',
    'description': """
    This module is used for Manufacturing BOM.
    """,
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'http://www.skyscendbs.com',
    'depends': ['base', 'mrp', 'contacts', 'sale_management', 'purchase'],
    'data': [
        'data/res_currency_data.xml',
        'views/mrp_bom_view.xml',
        'views/mrp_routing_workcenter_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
