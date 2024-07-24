from odoo import api, models,fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    route_ids = fields.Many2many('stock.warehouse',string='Route')