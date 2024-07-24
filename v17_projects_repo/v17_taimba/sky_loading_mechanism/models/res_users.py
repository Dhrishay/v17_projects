# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overridden create method to add driver on the partner.
        ------------------------------------------------------
        @param self: object pointer
        @param vals_lst: List of dictionaries
        :return: recordset
        """
        user = super(ResUsers, self).create(vals_list)
        if user.user_type == 'driver':
            user.partner_id.is_drivers = True
        return user

    def write(self, vals):
        """
        Overridden write method to add driver on the partner.
        -----------------------------------------------------
        @param self: object pointer
        @param vals: Dictionary containing fields and values
        :return: True
        """
        res = super(ResUsers, self).write(vals)
        if vals.get('user_type', False) and vals['user_type'] == 'driver':
            self.partner_id.is_drivers = True
        return res