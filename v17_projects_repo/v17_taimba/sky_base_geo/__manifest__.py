{
    'name': 'Base Geo',
    'version': '17.0.0.0.1',
    'category': 'other',
    'summary': '',
    'author': 'Skyscend Business Solutions',
    'website': 'http://www.skyscendbs.com',
    'description': "Base Geo",
    'depends': ['contacts', 'sale_management', 'base_address_extended'],
    'data': [
        'security/ir.model.access.csv',
        'security/sky_security.xml',
        'views/area_details_view.xml',
        'views/res_partner_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
