# -*- encoding: utf-8 -*-

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    bom_name = fields.Char(string='Name')
