# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Types of Customer'
    _rec_name = 'customer_type'

    customer_type = fields.Char('Customer Type')
