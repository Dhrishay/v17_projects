from odoo import api, models,fields

class Product(models.Model):
    _inherit = 'product.product'

    route_id = fields.Many2one('stock.warehouse','Route')