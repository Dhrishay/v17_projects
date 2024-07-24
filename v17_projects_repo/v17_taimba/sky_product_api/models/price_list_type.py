# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import api, models,fields


class Productpriclist(models.Model):
    _inherit = 'product.pricelist'

    customer_type_id = fields.Many2one('customer.type', string='Customer Type')



