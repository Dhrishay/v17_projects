from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """
        This method will set route, driver and vehicle on the shipment.
        ---------------------------------------------------------------
        @param self: object pointer
        """
        res = super(SaleOrder, self)._action_confirm()
        for so in self:
            for picking in so.picking_ids:
                picking.write({
                    'driver_id': so.driver_id.id,
                    'vehicle_id': so.vehicle_id.id,
                    'route_id': so.route_id.id
                })
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        Overridden the _Create_invoice method to add driver, vehicle and route.
        -----------------------------------------------------------------------
        @param grouped:
        @param final:
        @param date:
        :return: recordset of invoices
        """
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
        for so in self:
            for inv in so.invoice_ids:
                inv.write({
                    'vehicle_id': so.vehicle_id.id,
                    'driver_id': so.driver_id.id,
                    'route_id': so.route_id.id
                })
        return invoices

