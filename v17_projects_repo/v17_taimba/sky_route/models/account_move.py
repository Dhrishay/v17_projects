from odoo import api, models,fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    route_id = fields.Many2one('stock.warehouse','Route')