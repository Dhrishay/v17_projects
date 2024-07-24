# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Inherit Sale Order Model."""
    _inherit = 'sale.order'

    # Rewrite This field because make it independent module.
    route_id = fields.Many2one('stock.warehouse', 'Route')
    cart_quantity = fields.Float(compute='_compute_cart_info', string='Cart Quantity')

    @api.model
    def _compute_is_so_expiry(self):
        self.is_so_expiry = self.env['ir.config_parameter'].sudo(). \
            get_param('sybyl_cancel_quotation_after_expire.so_expiry')

    is_so_expiry = fields.Boolean('Is Expiry', compute=_compute_is_so_expiry,
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                   'sybyl_cancel_quotation_after_expire.so_expiry'))

    def cancel_quotation(self):
        """Cancel Expired Sales Quotation using Cron."""
        expire_quotation = self.sudo().search([('state', '=', 'draft')])

        for rec in expire_quotation:
            hours = 0
            if rec.is_so_expiry:
                config_hours = rec.env['ir.config_parameter'].sudo(). \
                                   get_param('sybyl_cancel_quotation_after_expire.so_expiration_hours') or 0
                if rec.date_order:
                    diff = (datetime.now() - rec.date_order)
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                if float(config_hours) <= hours:
                    rec.action_cancel()

    def action_confirm(self):
        for rec in self:
            for line in rec.order_line:
                if line.product_id.type != 'service':
                    stock_location = self.env['stock.location'].search([("id", "=", rec.warehouse_id.lot_stock_id.id)])
                    stock_quant = self.env['stock.quant'].search([('product_id', '=', line.product_id.id),
                                                                  ('location_id', '=', stock_location.id),
                                                                  ('company_id', '=', rec.company_id.id),
                                                                  ])
                    avail_qty = 0
                    for quant in stock_quant:
                        avail_qty += (quant.available_quantity > 0 and quant.available_quantity) or 0
                    if avail_qty < line.product_uom_qty:
                        raise UserError(_('Insufficient Stock Please Update Your Stock for product(%s).') % (line.product_id.name))
        return super().action_confirm()

    # //Cart Update

    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_cart_info(self):
        for order in self:
            order.cart_quantity = "%.2f" % float(sum(order.mapped('website_order_line.product_uom_qty')))
            order.only_services = all(l.product_id.type in ('service', 'digital') for l in order.website_order_line)

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        print ("INNNNNNNNNNNNNNN", kwargs, product_id)
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)
        # change lang to get correct name of attributes/values
        product_with_context = self.env['product.product'].with_context(product_context)
        product = product_with_context.browse(int(product_id)).exists()
        print ("productproductproduct", product, product._is_add_to_cart_allowed())
        if not product or (not line_id and not product._is_add_to_cart_allowed()):
            raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0.0
        order_line = False
        if self.state != 'draft':
            request.session['sale_order_id'] = None
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
        if line_id is not False:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]

        # Create line if no line with product_id can be located
        if not order_line:
            no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
            received_no_variant_values = product.env['product.template.attribute.value'].browse(
                [int(ptav['value']) for ptav in no_variant_attribute_values])
            received_combination = product.product_template_attribute_value_ids | received_no_variant_values
            product_template = product.product_tmpl_id

            # handle all cases where incorrect or incomplete data are received
            combination = product_template._get_closest_possible_combination(received_combination)

            # get or create (if dynamic) the correct variant
            product = product_template._create_product_variant(combination)

            if not product:
                raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

            product_id = product.id

            values = self._cart_find_product_line(self.id, product_id, qty=1)

            # add no_variant attributes that were not received
            for ptav in combination.filtered(
                    lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
                no_variant_attribute_values.append({
                    'value': ptav.id,
                })

            # save no_variant attributes values
            if no_variant_attribute_values:
                values['product_no_variant_attribute_value_ids'] = [
                    (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
                ]

            # add is_custom attribute values that were not received
            custom_values = kwargs.get('product_custom_attribute_values') or []
            received_custom_values = product.env['product.template.attribute.value'].browse(
                [int(ptav['custom_product_template_attribute_value_id']) for ptav in custom_values])

            for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav not in received_custom_values):
                custom_values.append({
                    'custom_product_template_attribute_value_id': ptav.id,
                    'custom_value': '',
                })

            # save is_custom attributes values
            if custom_values:
                values['product_custom_attribute_value_ids'] = [(0, 0, {
                    'custom_product_template_attribute_value_id': custom_value[
                        'custom_product_template_attribute_value_id'],
                    'custom_value': custom_value['custom_value']
                }) for custom_value in custom_values]

            order_line = SaleOrderLineSudo.create(values)

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        if set_qty:
            quantity = set_qty
        elif add_qty is not None:

            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            linked_line = order_line.linked_line_id
            order_line.unlink()
            if linked_line:
                # update description of the parent
                linked_product = product_with_context.browse(linked_line.product_id.id)
                linked_line.name = linked_line.get_sale_order_line_multiline_description_sale(linked_product)
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in
                                                 order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra))._cart_find_product_line(
                self.id, product_id, qty=quantity)
            order = self.sudo().browse(self.id)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                })
            product_with_context = self.env['product.product'].with_context(product_context).with_company(
                order.company_id.id)
            product = product_with_context.browse(product_id)

            order_line.write(values)

            # link a product to the sales order
            if kwargs.get('linked_line_id'):
                linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id': linked_line.id,
                })
                linked_product = product_with_context.browse(linked_line.product_id.id)
                linked_line.name = linked_line.get_sale_order_line_multiline_description_sale(linked_product)
            # Generate the description with everything. This is done after
            # creating because the following related fields have to be set:
            # - product_no_variant_attribute_value_ids
            # - product_custom_attribute_value_ids
            # - linked_line_id
            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

        option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)
        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}

