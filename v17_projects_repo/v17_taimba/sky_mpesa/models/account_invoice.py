# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    mpesa_id = fields.Many2one("mpesa.payment", 'Mpesa ID')

