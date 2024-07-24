# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import models, fields, api


class DriverVehicle(models.Model):
    _inherit = "sale.order"

    driver_id = fields.Many2one('res.partner', 'Driver')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
#     route_id = fields.Many2one('stock.warehouse', 'Route')
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        for sale_rec in self:
            if sale_rec.vehicle_id:
                warehouse_id = self.env['stock.warehouse'].search([('name', '=', sale_rec.vehicle_id.name)])
                if warehouse_id:
                    sale_rec.warehouse_id = warehouse_id
                else:
                    sale_rec._compute_warehouse_id()
                sale_rec.driver_id = sale_rec.vehicle_id.driver_id
            else:
                sale_rec.driver_id = False

    def delete_customers(self):
        # archive customers without sales, invoices and purchases
        partner_obj = self.env['res.partner']
        move_line_obj = self.env['account.move.line']
        contacts = partner_obj.search([])
        p_list = []
        contacts = partner_obj.search(
            [('customer_rank', '>', 0)]).filtered(
            lambda x: not x.sale_order_ids and not x.invoice_ids and
                      x.purchase_order_count == 0 and x.supplier_invoice_count == 0)
        for contact in contacts:
            move_line_ids = move_line_obj.search([('partner_id', '=', contact.id)])
            # Few customer doesn't have sales, purchases but does have move lines(allownces from payslips)
            if move_line_ids:
                pass
            else:
                contact.active = False

    def contact_route(self):
        partner_obj = self.env['res.partner']
        for contact in partner_obj.search([]):
            last_order = self.search([('partner_id', '=', contact.id), ('user_id', '!=', False)],
                                     order='date_order desc', limit=1)
            if last_order:
                if last_order.user_id.route_ids:
                    contact.write(
                        {'route_id': last_order.user_id.route_ids and last_order.user_id.route_ids[0] or False})

