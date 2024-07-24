from odoo import fields, models, api


class OrderStatus(models.Model):
    _inherit = 'sale.order'

    route_id = fields.Many2one('stock.warehouse', 'Route')

    @api.onchange('partner_id', 'route_id')
    def onchange_salesperson(self):
        self.route_id = self.partner_id.route_id.id
