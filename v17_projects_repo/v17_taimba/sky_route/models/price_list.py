from odoo import api, models,fields

class Productpriclist(models.Model):
    _inherit = 'product.pricelist'

    route_id = fields.Many2one('stock.warehouse','Route')