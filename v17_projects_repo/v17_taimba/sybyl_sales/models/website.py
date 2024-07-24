# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import api, fields, models, _


class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner_sudo):
        res = super()._prepare_sale_order_values(partner_sudo)
        if not res.get('user_id'):
            ir_model_data = self.env['ir.model.data']
            categ_id = ir_model_data.check_object_reference('sybyl_sales', 'crm_category_customer')[1]
            res.update({'tag_ids': [(6, 0, [categ_id])]})
        return res
