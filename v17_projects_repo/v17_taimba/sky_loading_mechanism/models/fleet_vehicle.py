# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    warehouse_id = fields.Many2one('stock.warehouse', 'Related Warehouse')

    @api.model_create_multi
    def create(self, vals_lst):
        stock_warehouse_object = self.env["stock.warehouse"]
        fleet_vehicle = super(FleetVehicle, self).create(vals_lst)
        warehouse = stock_warehouse_object.create({'name': fleet_vehicle.brand_id.name + '/' + fleet_vehicle.model_id.name + "/" + fleet_vehicle.license_plate,
                                       'code': fleet_vehicle.license_plate,
                                       "vehicle": True})
        fleet_vehicle.write({
            'warehouse_id': warehouse.id
        })
        return fleet_vehicle

    # OVERRIDE WareHouse Inactive
    def write(self, vals):
        res = super(FleetVehicle, self).write(vals)
        if 'active' in vals:
            for vehicle in self:
                if vehicle.active is True:
                    vehicle.warehouse_id.active = True
                elif vehicle.active is False:
                    vehicle.warehouse_id.active = False
        return res

    def unlink(self):
        for vehicle in self:
            vehicle.warehouse_id.active=False
        return super(FleetVehicle, self).unlink()