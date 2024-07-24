from odoo import api, models,fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    route_id = fields.Many2one('stock.warehouse','Route')