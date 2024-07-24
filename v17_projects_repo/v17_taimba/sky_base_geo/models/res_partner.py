from odoo import fields, models, api, _
import requests
from odoo.exceptions import RedirectWarning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    area_id = fields.Many2one(related='partner_id.area_id', store=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    area_id = fields.Many2one(related='order_id.area_id', store=True)


class Area(models.Model):
    _name = 'area.area'
    _description = 'Area'
    
    name = fields.Char("Name")
    code = fields.Char("Code")


class ResUser(models.Model):
    _inherit = "res.users"
    area_id = fields.Many2one(related='partner_id.area_id', store=True, readonly=False)


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    area_id = fields.Many2one('area.area', 'Area')
