from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'
    
    partner_categ_id = fields.Many2one('res.partner.category', string="Category")