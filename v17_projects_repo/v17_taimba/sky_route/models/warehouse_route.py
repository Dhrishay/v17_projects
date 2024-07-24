from odoo import fields, models, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    route=fields.Boolean('Route?')