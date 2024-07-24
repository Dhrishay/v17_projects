# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import models,fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_id = fields.Many2one('res.partner', 'Driver')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    loading_id = fields.Many2one('stock.loading')