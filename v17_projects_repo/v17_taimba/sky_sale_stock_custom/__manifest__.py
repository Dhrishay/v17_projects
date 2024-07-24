{
    'name': 'Sale Stock custom',
    'summary': 'Update Route, Driver and Vehicle on Delivery and Invoice',
    'category': '',
    'version': '17.0.0.1',
    'author': 'Skyscend Business Solutions Pvt. Ltd.',
    'website': 'www.skyscendbs.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale_management',
        'sky_route',
        'sky_loading_mechanism',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/user_target.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
