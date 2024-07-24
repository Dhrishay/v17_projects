# -*- encoding: utf-8 -*-
##########################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions Pvt. Ltd. (https://www.skyscendbs.com)
#
##########################################################################################
from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string=" Is Customer ?")
    is_vendor = fields.Boolean(string=" Is Vendor ?")

    @api.onchange('customer_rank')
    def change_customer_rank(self):
        """
        On change of customer rank field, update Is Customer true if customer rank is greater than zero
        """
        for rec in self:
            if rec.customer_rank > 0:
                rec.is_customer = True

    @api.onchange('supplier_rank')
    def change_supplier_rank(self):
        """
        On change of supplier rank field, update Is Supplier true if supplier rank is greater than zero
        """
        for rec in self:
            if rec.supplier_rank > 0:
                rec.is_vendor = True

    @api.onchange('is_customer')
    def change_customer_rank_flag(self):
        """
           On change of is customer, if is customer is true increase customer rank else update it with zero.
        """
        for rec in self:
            if rec.is_customer:
                rec._increase_rank('customer_rank')
            if rec.is_customer == False:
                rec.customer_rank = 0

    @api.onchange('is_vendor')
    def change_supplier_rank_flag(self):
        """
           On change of is supplier,if is supplier is true increase supplier rank else update it with zero.
        """
        for rec in self:
            if rec.is_vendor:
                rec._increase_rank('supplier_rank')
            if rec.is_vendor == False:
                rec.supplier_rank = 0

    def compute_domain(self, type):
        """
         Append Is customer true domain if customer invoice/refund/receipt else append Is vendor true domain
        :param type: Type of Invoice/refund/receipt
        :return: Domain
        """
        if type in ['out_invoice', 'out_refund', 'out_receipt', 'inbound']:
            domain = [('is_customer', '=', True)]
        else:
            domain = [('is_vendor', '=', True)]
        return domain

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        """
            Override _name_search in order to add domain of Is customer and Is vendor fields.
        """
        if self._context.get('move_type'):
            domain += self.compute_domain(self._context.get('move_type'))
        elif self._context.get('payment_type'):
            domain += self.compute_domain(self._context.get('payment_type'))
        return super(Partner, self)._name_search(name, domain=domain, operator=operator, limit=limit,
                                                 order=order)


    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, access_rights_uid=None):
    #     """
    #         Override _search in order to grep search on Is customer and Is vendor fields.
    #     """
    #     if self._context.get('move_type'):
    #         args += self.compute_domain(self._context.get('move_type'))
    #     elif self._context.get('payment_type'):
    #         args += self.compute_domain(self._context.get('payment_type'))
    #     return super(Partner, self)._search(args, offset=offset, limit=limit, order=order,
    #                                         access_rights_uid=access_rights_uid)
