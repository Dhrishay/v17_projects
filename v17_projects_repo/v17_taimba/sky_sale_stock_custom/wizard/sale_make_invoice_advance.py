from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoices(self, order, so_line, amount):
        """
        This method is overridden to add route, driver and vehicle on the invoice from sale order
        -----------------------------------------------------------------------------------------
        @param order: Sale Order
        @param so_line: Sale Order Line
        @param amount:
        :return: recordset of invoice.
        """
        inv = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        inv.write({
            'vehicle_id': order.vehicle_id.id,
            'route_id': order.route_id.id,
            'driver_id': order.driver_id.id
        })
        return inv
