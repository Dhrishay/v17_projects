from odoo import api, models,fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    route_id = fields.Many2one('stock.warehouse','Route')