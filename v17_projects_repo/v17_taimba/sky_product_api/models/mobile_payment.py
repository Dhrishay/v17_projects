# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class MobilePayment(models.Model):
    _inherit = 'account.journal'

    payment_for_mobile = fields.Boolean('For Mobile App')
    till_number = fields.Char("Till No.")
