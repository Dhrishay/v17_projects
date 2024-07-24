# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    driver_id = fields.Many2one('res.partner', 'Driver', tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', tracking=True)
    route_id = fields.Many2one('stock.warehouse', 'Route')
