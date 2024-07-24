# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class OrderStatus(models.Model):
    _inherit = 'sale.order'

    sale_status = fields.Selection([
        ('pending', 'Pending'),
        ('cancel', 'Cancelled'),
        ('fulfill', 'Fulfilled'),
    ], default='pending', copy=False, readonly=True, string="Order Status")

    def action_cancel(self):
        rec = super(OrderStatus,self).action_cancel()
        self.write({'sale_status': 'cancel'})
        return rec

    def action_draft(self):
        draft = super(OrderStatus, self).action_draft()
        self.write({'sale_status': 'pending'})
        return draft

    def update_sale_satus(self):
        for rec in self:
            if rec.picking_ids:
                for move in self.filtered(lambda m:m.state in ('sale')):
                    #updating sale order status
                    rec.sale_status = 'fulfill'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        rec = super(StockPicking,self).button_validate()
        dar = self.env['sale.order'].search([('id','=',self.sale_id.id)])
        if self.state == 'done':
            dar.write({'sale_status': 'fulfill'})
        return rec



