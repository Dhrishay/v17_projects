# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         fields = res.get('fields')
    #         print ("fieldsfieldsfields", fields)
    #         if fields:
    #             if fields.get('partner_id') and self._context.get('default_move_type') == 'out_invoice':
    #                 res['fields']['partner_id']['domain'] = "[('customer_rank','>',0),('company_id','in',[company_id,False])]"
    #             if fields.get('partner_id') and self._context.get('default_move_type') == 'in_invoice':
    #                 res['fields']['partner_id']['domain'] = "[('supplier_rank','>',0),('company_id','in',[company_id,False])]"
    #     return res


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange('payment_type')
    def change_payment_type(self):
        res = {}    
        for rec in self:
            if rec.payment_type == 'inbound':
                res['domain'] = {'partner_id':[('customer_rank', '>', 0)]}
            if rec.payment_type == 'outbound':
                res['domain'] = {'partner_id':[('supplier_rank', '>', 0)]}
        return res