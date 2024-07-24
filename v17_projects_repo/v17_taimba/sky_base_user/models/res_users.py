# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_type = fields.Selection([('driver', 'Salesrep'),
                                  ('customer', 'Customer'),
                                  ('sales_rep', 'Presaller')],
                                 default='customer')
