# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    mpesa_shortcode = fields.Char(string="Mpesa Short Code")
    route_ids = fields.Many2many('stock.warehouse', domain=[('route', '=', True)])
    mpesa_reconciliation = fields.Boolean("Mpesa Reconciliation")
