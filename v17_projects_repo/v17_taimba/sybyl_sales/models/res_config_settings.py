# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_expiry = fields.Boolean(
        'Quotation Expiry',
        config_parameter='sybyl_cancel_quotation_after_expire.so_expiry',
       )

    so_expiration_hours = fields.Float(
        string='Quotation Cancel After Days',
        config_parameter='sybyl_cancel_quotation_after_expire.so_expiration_hours')
