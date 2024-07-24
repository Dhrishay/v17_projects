# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import random
import string
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime


class LoadingMechanism(models.Model):
    _name = 'stock.loading'
    _description = 'Description'
    _rec_name = 'sequence_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ], 'State', default='draft', tracking=True)
    sequence_id = fields.Char("ID", copy=False, index=True)
    type = fields.Selection([
        ('loading', 'Loading'),
        ('unloading', 'Unloading')], 'Type')
    source_warehouse_id = fields.Many2one("stock.warehouse", string="Source", tracking=True)
    destination_warehouse_id = fields.Many2one("stock.warehouse", string="Destination", tracking=True)
    driver_id = fields.Many2one("res.partner", string="Driver", tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', tracking=True)
    date = fields.Datetime('Date', tracking=1, default=fields.Datetime.now)
    stock_loading_unloading_lines = fields.One2many('stock.loading.lines', inverse_name='stock_loading_id',
                                                    string='Products')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_loading_ids')
    picking_ids = fields.One2many('stock.picking', 'loading_id', string='Transfers')
    handshaketoken = fields.Char("HandShake Token")
    post_true = fields.Boolean("Posted from API", default=False)


    def unlink(self):
        for load in self:
            if load.state == 'confirmed':
                raise UserError(_("You can't delete data in confirmed state"))
        rec = super(LoadingMechanism, self).unlink()
        return rec


    @api.onchange('vehicle_id')
    def onchange_vehicle(self):
        if not self.vehicle_id:
            # self.source_warehouse_id = False
            self.stock_loading_unloading_lines = [(6, 0, [])]
        warehouse_id = self.env["stock.warehouse"].search_read([("name", '=', self.vehicle_id.name)])
        self.driver_id = self.vehicle_id.driver_id
        if self.vehicle_id and self.type == "unloading":
            if warehouse_id:
                self.source_warehouse_id = warehouse_id[0]['id']
            else:
                self.source_warehouse_id = False
        elif self.vehicle_id and self.type == "loading":
            if warehouse_id:
                self.destination_warehouse_id = warehouse_id[0]['id']
            else:
                self.destination_warehouse_id = False

        if self.type == "unloading":
            stock_warehouse = self.env['stock.warehouse'].search([("id", "=", self.source_warehouse_id.id)])
            stock_location = self.env['stock.location'].search([("id", "=", stock_warehouse.lot_stock_id.id)])
            stock_quant = self.env['stock.quant'].search([("location_id", "=", stock_location.id)])
            lines = []
            unloading_obj = self.env['stock.loading.lines']
            for item in stock_quant:
                if item.quantity:
                    line_rec = unloading_obj.create({
                        'product_id': item.product_id.id,
                        'lot_id': item.lot_id.id,
                        'quantity': item.quantity,
                        'stock_loading_id': self.id
                    })
                    lines.append(line_rec.id)
            if lines:
                self.stock_loading_unloading_lines = [(6, 0, lines)]
            else:
                self.stock_loading_unloading_lines = [(6, 0, [])]

    @api.depends('picking_ids')
    def _compute_loading_ids(self):
        for loadin_rec in self:
            loadin_rec.delivery_count = len(loadin_rec.picking_ids)

    def action_view_delivery_loading(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        if self.type == "loading":
            picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        else:
            picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'incoming')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        return action

    def confirm_mechanism(self):
        picking_obj = self.env["stock.picking"]
        if self.type == "loading":
            operation_type = self.env["stock.picking.type"].search([("warehouse_id", '=', self.source_warehouse_id.id),
                                                                    ("code", "=", "outgoing")], limit=1)
            seq = self.env['ir.sequence'].next_by_code('loading.sequences')
            self.sequence_id = seq
        elif self.type == "unloading":
            operation_type = self.env["stock.picking.type"].search(
                [("warehouse_id", '=', self.destination_warehouse_id.id),
                 ("code", "=", "incoming")],
                limit=1)
            seq = self.env['ir.sequence'].next_by_code('unloading.sequences')
            self.sequence_id = seq
        stock_move_ids = []
        if not self.stock_loading_unloading_lines:
            raise UserError(_('Please add Lines first!'))
        for lines in self.stock_loading_unloading_lines:
            stock_move_id = self.env["stock.move"].create({"product_id": lines.product_id.id,
                                                           "location_id": self.source_warehouse_id.lot_stock_id.id,
                                                           "name": 'Loading ' + str(
                                                               lines.product_id.name),
                                                           "product_uom": lines.product_id.uom_id.id,
                                                           "product_uom_qty": lines.quantity,
                                                           "location_dest_id": self.destination_warehouse_id.lot_stock_id.id,
                                                           })
            stock_move_ids.append(stock_move_id.id)

        stock_picking_record = picking_obj.create({"origin": self.sequence_id,
                                                   "location_id": self.source_warehouse_id.lot_stock_id.id,
                                                   "picking_type_id": operation_type.id,
                                                   "scheduled_date": self.date,
                                                   "driver_id": self.driver_id.id,
                                                   "vehicle_id": self.vehicle_id.id,
                                                   "location_dest_id": self.destination_warehouse_id.lot_stock_id.id,
                                                   "move_type": "direct",
                                                   "loading_id": self.id,
                                                   "move_ids_without_package": [(6, 0,
                                                                                 stock_move_ids)]
                                                   },)
        for move in stock_picking_record.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
            if move.product_uom_qty > move.product_id.qty_available:
                raise UserError(stock_picking_record._get_without_quantities_error_message())

        stock_picking_record.action_assign()
        stock_picking_record.action_confirm()
        stock_picking_record.button_validate()
        self.state = 'confirmed'
        return True

    @api.model
    def default_get(self, fields):
        res = super(LoadingMechanism, self).default_get(fields)
        warehouse = self.env.ref('stock.warehouse0').id
        if self.env.context.get("default_type") == "loading":
            res.update({"source_warehouse_id": warehouse})
        if self.env.context.get("default_type") == "unloading":
            res.update({"destination_warehouse_id": warehouse})
        return res

    @api.model_create_multi
    def create(self, fields):
        res = super(LoadingMechanism, self).create(fields)
        res.update({
                    "handshaketoken": ''.join(random.choices(string.ascii_lowercase + 
                                                             string.digits, k=15))})
        return res

# class Stockproduction(models.Model):
#
#     _inherit = 'stock.production.lot'
#
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike', limit=None):
#         res = self.search(args, limit=None)
#         if self.env.context.get('available_lot'):
#             res=res.filtered(lambda l: l.product_qty > 0)
#         return res.name_get()