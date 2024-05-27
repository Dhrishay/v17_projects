from odoo import fields, models


class MrpRouting(models.Model):
    _inherit = 'mrp.routing.workcenter'

    code = fields.Char("Code")
