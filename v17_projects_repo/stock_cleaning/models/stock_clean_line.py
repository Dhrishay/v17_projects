from odoo import fields, models


class StockCleanLine(models.Model):
    _name = 'stock.clean.line'

    stock_clean_id = fields.Many2one('stock.location.clean', string='Stock Clean')
    product_id = fields.Many2one('product.product', string='Product')
    lot_serial_id = fields.Many2one('stock.lot', string='Serial Number')
    time_of_production = fields.Char('Time Of Production')
    total_weight = fields.Char('Total Weight')
    sale_order_id = fields.Many2one('sale.order',string='Sale Order Number')
    purchase_order_id = fields.Many2one('purchase.order',string='Purchase Order Number')
    partner_id = fields.Char('Client/Vendor')
