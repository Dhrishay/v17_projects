# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
import re
from odoo import http, _, tools
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.exceptions import Forbidden


class WebsiteSale(WebsiteSale):

    @http.route("/partner/billingAddress", type="json", auth="user", website=True)
    def partner_billing_address(self, route_id):
        if route_id:
            request.env.user.partner_id.write({'route_id': int(route_id)})
            return True
        else:
            return False

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ('new', 'shipping')
                        partner_id = -1
                    elif partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":

            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id
                route = Partner.sudo().browse(partner_id).route_id
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.route_id = route and route.id or False
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                 mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                    # We need to update the pricelist(by the one selected by the customer), because onchange_partner reset it
                    # We only need to update the pricelist when it is not redirected to /confirm_order
                    if kw.get('callback', False) != '/shop/confirm_order':
                        request.website.sale_get_order(update_pricelist=True)
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id
                    order.route_id = route and route.id or False
                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        render_values.update(self._get_route_related_render_values(kw, render_values))
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    def _get_route_related_render_values(self, kw, render_values):
        values = render_values['checkout']
        order = render_values['website_sale_order']
        def_route_id = order.partner_id.route_id
        route = 'route_id' in values and values['route_id'] != '' and request.env['stock.warehouse'].browse(
            int(values['route_id']))
        route = route and route.exists() or def_route_id

        res = {
            'route': route,
            'routes': request.env['stock.warehouse'].sudo().search([('route', '=', True)]),
        }
        return res

    def _get_mandatory_billing_fields(self):
        return ["name", "country_id", "phone"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "country_id", "phone"]

    def _get_mandatory_fields_billing(self, country_id=False):
        res = super()._get_mandatory_fields_billing(country_id)
        if 'zip' in res:
            res.remove('zip')
        return res

    def _get_mandatory_fields_shipping(self, country_id=False):
        res = super()._get_mandatory_fields_shipping(country_id)
        if 'zip' in res:
            res.remove('zip')
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error,error_message = super().checkout_form_validate(mode, all_form_values, data)
        # prevent Phone Number is Duplicate
        if data.get('phone'):
            partner = request.env['res.partner'].sudo().search([('phone','=',data.get('phone'))])
            if partner.exists():
                error['phone'] = 'Duplication'
                error_message.append(_('Phone Number is already registered, Please enter any other phone number.'))
        return error, error_message

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg = super().values_postprocess(order, mode, values, errors, error_msg)
        new_values["route_id"] = values.get('route_id')
        return new_values, errors, error_msg
