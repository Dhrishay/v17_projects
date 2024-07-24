from odoo import models, fields


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    category_id = fields.Many2one('res.partner.category', string="Category")