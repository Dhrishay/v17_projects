# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models


class LoadingUnloadingLines(models.Model):
    _name = 'stock.loading.lines'
    _description = 'Description'

    stock_loading_id = fields.Many2one("stock.loading", "Stock Loading")
    product_id = fields.Many2one("product.product", 'Product Name')
    # lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial')
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial')
    quantity = fields.Float("Quantity")
