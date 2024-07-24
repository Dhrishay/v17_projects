# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import http
from odoo.http import Response, request
from odoo.addons.sky_base_api.common import invalid_response, valid_response
import functools
import string
import random
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime as dt
import pytz


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.env = request.env(user=request.session.uid)
        return func(self, *args, **kwargs)

    return wrap


class GetDetails(http.Controller):

    @validate_token
    @http.route('/ProductList', type='json', auth='user')
    def get_products(self):
        fields = ['id', 'name', 'description', 'list_price', 'image_128']
        product_template_rec = request.env['product.product'].sudo().search_read([], fields=fields, offset=[], order='id')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in product_template_rec:
            record['image_128'] = base_url + "/web/image?model=product.product&id=" + str(
                record['id']) + "&field=image_128"
        return product_template_rec

    @validate_token
    @http.route('/ProductListByRouteID', type='json', auth='user')
    def get_products_by_route(self, route_id):
        fields = ['id', 'name', 'description', 'list_price', 'image_128']
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        pricelist_data = request.env['product.pricelist'].search([('route_id', '=', route_id), ('name','=','Public Pricelist')], limit=1)
        product_template_main = request.env['product.product'].search_read([], fields=fields,
                                                                           order='id')
        product_obj = request.env["product.product"]
        for product_rec in product_template_main:
            product_price = product_obj.browse(product_rec.get('id')).with_context(pricelist=pricelist_data.id).lst_price
            product_rec.update({"pricelist_price": product_price})
            product_rec['image_128'] = base_url + "/web/image?model=product.product&id=" + str(
                product_rec['id']) + "&field=image_128"
        return product_template_main

    @validate_token
    @http.route('/PaymentMethodsbyRoute', type='json', auth='user')
    def getpaymethodsbyroute(self, route_id):
        fields = ['id', 'name', 'mpesa_shortcode', 'till_number']
        payment_methods = request.env['account.journal'].sudo().search_read(
            [('type', 'in', ['bank', 'cash']), ('payment_for_mobile', '=', True),
             ('route_ids', 'in', [route_id])], fields=fields, offset=[],
            order='id')
        return payment_methods

    @validate_token
    @http.route('/PaymentMethod', type='json', auth='user')
    def get_payment_methods(self):
        fields = ['id', 'name', 'mpesa_shortcode', 'till_number']
        payment_methods = request.env['account.journal'].search_read(
            [('type', 'in', ['bank', 'cash']), ('payment_for_mobile', '=', True)], fields=fields, offset=[],
            order='id')
        return payment_methods

    @validate_token
    @http.route('/Routes', type='json', auth='user')
    def get_routes(self):
        fields = ['id', 'name']
        route_data = request.env['stock.warehouse'].search_read([('route', '=', True)],
                                                                fields=fields,
                                                                offset=[],
                                                                order='id')
        return route_data

    @validate_token
    @http.route('/CustomerDetails', type='json', auth='user')
    def get_customers(self, route_id):
        fields = ['id', 'name', 'phone', 'route_id', 'partner_latitude', 'partner_longitude']
        customer_data = request.env['res.partner'].search_read([('customer_rank', '>', 0),
                                                                ('route_id', '=', route_id)],
                                                               fields=fields, offset=[],
                                                               order='id')
        return customer_data

    @validate_token
    @http.route('/GetOrders', type='json', auth='user')
    def get_sale_orders(self, route_id, date=False):
        fields = ['id', 'name', 'partner_id', 'sale_status', 'date_order', 'amount_total', 'order_line']
        domain = [('route_id', '=', route_id), ('state', '!=', 'cancel')]
        if date:
            st_time = date + ' 00:00:00'
            en_time = date + ' 23:59:59'
            st_dt = dt.strptime(st_time, DEFAULT_SERVER_DATETIME_FORMAT)
            en_dt = dt.strptime(en_time, DEFAULT_SERVER_DATETIME_FORMAT)
            local = pytz.timezone(request.env.context.get('tz'))
            local_st_dt = local.localize(st_dt, is_dst=None)
            utc_st_dt = local_st_dt.astimezone(pytz.utc)
            local_en_dt = local.localize(en_dt, is_dst=None)
            utc_en_dt = local_en_dt.astimezone(pytz.utc)
            domain += [('date_order', '>=', utc_st_dt), ('date_order', '<=', utc_en_dt)]
        sale_data = request.env['sale.order'].search_read(domain,
                                                          fields=fields, offset=[],
                                                          order='date_order desc')
        for orders in sale_data:
            order_partner = orders.get('partner_id')
            partner = request.env['res.partner'].browse([order_partner[0]])
            partner_latitude = partner.partner_latitude
            partner_longitude = partner.partner_longitude
            order_amount = orders.get('amount_total')
            order = request.env['sale.order'].browse([orders.get('id')])
            remaining_amount = 0.0
            for payment in order.invoice_ids:
                remaining_amount += payment.amount_residual
            payment_amount = order_amount - remaining_amount
            if order_amount == payment_amount:
                message = "Paid"
            else:
                message = "Partial Paid"
            orders.update(
                {'Order Amount': order_amount, 'Payment Amount': payment_amount, 'Remaining Payment': remaining_amount,
                 'Payment Status': message, 'Partner Latitude': partner_latitude,
                 'Partner Longitude': partner_longitude})
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for records in sale_data:
            custom_array = []
            for line_id in request.env['sale.order.line'].browse(records["order_line"]):
                custom_array.append({'product_id': line_id.product_id.id,
                                     'name': line_id.product_id.name,
                                     'quantity': line_id.product_uom_qty,
                                     'price_subtotal': line_id.price_subtotal,
                                     'image': base_url + "/web/image?model=product.product&id=" + str(
                line_id.product_id.id) + "&field=image_128"})
            records["order_line"] = custom_array
        return sale_data

    @http.route('/RegisterCustomer', type='json', auth='public', cors='*')
    def post_customer_eccomerce(self, name=False, phone_number=False, email=False, firstname=False, lastname=False, route_id=False,
                              customer_type_id=False, partner_latitude=False, partner_longitude=False, password=False):
        result = {}
        try:
            customer = request.env['res.partner']
            new_customer = customer.sudo().create({'display_name': name,
                                                       'phone': phone_number,
                                                       'email': email,
                                                       'firstname': firstname,
                                                       'lastname': lastname,
                                                       'route_id': route_id,
                                                       'customer_rank': 1,
                                                       'partner_latitude': partner_latitude,
                                                       'partner_longitude': partner_longitude,
                                                       'is_customer': True,
                                                       'customer_type_id': customer_type_id})
            group_portal = request.env.ref('base.group_portal')
            if new_customer:
                existing_user = request.env['res.users'].sudo().search_read([('email', '=', email)])
                if existing_user:
                    result.update({'message': 'You can not have two users with the same login!', 'result': False})
                else:
                    user_id = request.env['res.users'].sudo().create({'partner_id': new_customer.id,
                                                            'email': email,
                                                            'login': email,
                                                            'route_ids': [(6,0,[route_id])],
                                                            'phone_number':phone_number,
                                                            'password':password,
                                                            'groups_id': [(4, group_portal.id)]
                                                            })

                    if user_id:
                        _token = request.env["api.access_token"]
                        access_token = _token.sudo().find_one_or_create_token(user_id=user_id.id, create=True)
                    result.update({'message': 'Successfully Created the Customer ' + new_customer.name,
                                    'id':new_customer.id,
                                    'user_id': user_id.id,
                                    'result': True})
        except Exception as e:
            result.update({'message': e, 'result': False})
            return result
        return result

    @validate_token
    @http.route('/PostCustomerDetails', type='json', auth='user')
    def post_customer_details(self, customer_id=False, name=False, phone_number=False, email=False, firstname=False, lastname=False, route_id=False,
                              customer_type_id=False, partner_latitude=False, partner_longitude=False):
        result = {}
        try:
            if not customer_id and (not name or not phone_number or not email or not firstname or not lastname or not route_id or not customer_type_id):
                result.update({'message': """When you're creating a customer you must pass the following fields.
                Name
                Phone Number
                Email
                FirstName
                LastName
                Route
                Customer Type""", 'result': False})
            if customer_id:
                customer = request.env['res.partner'].sudo().search([('id', '=', customer_id)], limit=1)
                update_vals = {}
                if name:
                    update_vals.update({
                        'display_name': name,
                    })
                if phone_number:
                    update_vals.update({
                        'phone': phone_number,
                    })
                if email:
                    update_vals.update({
                        'email': email,
                    })
                if firstname:
                    update_vals.update({
                        'firstname': firstname,
                    })
                if lastname:
                    update_vals.update({
                        'lastname': lastname,
                    })
                if route_id:
                    update_vals.update({
                        'route_id': route_id,
                    })
                if customer_type_id:
                    update_vals.update({
                        'customer_type_id': customer_type_id,
                    })
                if customer_type_id:
                    update_vals.update({
                        'partner_latitude': partner_latitude,
                    })
                if customer_type_id:
                    update_vals.update({
                        'partner_longitude': partner_longitude,
                    })
                customer.sudo().write(update_vals)
                result.update({'message': 'Successfully Updated the Customer ' + customer.name, 'result': True})
            else:
                customer = request.env['res.partner']
                new_customer = customer.sudo().create({'display_name': name,
                                                       'phone': phone_number,
                                                       'email': email,
                                                       'firstname': firstname,
                                                       'lastname': lastname,
                                                       'route_id': route_id,
                                                       'customer_rank': 1,
                                                       'partner_latitude': partner_latitude,
                                                       'partner_longitude': partner_longitude,
                                                       'is_customer': True,
                                                       'customer_type_id': customer_type_id})
                result.update({'message': 'Successfully Created the Customer ' + new_customer.name, 'result': True})
        except Exception as e:
            result.update({'message': e, 'result': False})
        return result

    @validate_token
    @http.route('/PostLogin', type='json', auth='user')
    def post_login(self, name, username, phone_number, route_id):
        N = 7
        password = ''.join(random.choices(string.ascii_uppercase + 
                                          string.digits, k=N))
        user = request.env['res.users']
        group_portal = request.env.ref('base.group_portal')
        user.sudo().create({'name': name,
                            'password': str(password),
                            'login': username,
                            'phone_number': phone_number,
                            'route_id': route_id,
                            'groups_id': [(4, group_portal.id)]
                            })
        return {"Phone number": phone_number,
                "Password": password}

    @validate_token
    @http.route('/AddRoute', type='json', auth='user')
    def add_route(self, user_id, route_id):
        request.env['res.users'].search([('id', '=', user_id)]).write({"route_id": route_id})
        return True

    # ecommerce
    @http.route('/ForgotPassword', type='json', auth='public', cors='*')
    def update_password(self, phone_number, new_passwd):
        user = request.env["res.users"].sudo().search(['|', ("phone_number", "=", phone_number), ('login', '=', phone_number)])
        if user:
            if new_passwd:
                user.sudo().write({'password': new_passwd})
                return {"message": "Password Updated Successfully!", "result": True, "user_id":user.id}
            return {"message": "Setting empty passwords is not allowed for security reasons!", "result": False}
        else:
            return {"message": "User does not exist! Kindly contact Administrator!", "result": False}

    @validate_token
    @http.route('/ResetPassword', type='json', auth='user')
    def reset_password(self, phone_number, new_passwd):
        user = request.env["res.users"].sudo().search([("phone_number", "=", phone_number)])
        if user:
            if new_passwd:
                user.sudo().write({'password': new_passwd})
                return {"message": "Password Updated Successfully!", "result": True}

            return {"message": "Setting empty passwords is not allowed for security reasons!", "result": False}
        else:
            return {"message": "User does not exist! Kindly contact Administrator!", "result": False}

    @http.route('/GetOrdersByPartner', type='json', auth='public', cors='*')
    def get_sale_orders_by_partner(self, partner_id, date=False):
        # partner_id = user_id in ecommerce
        user_rec = request.env['res.users'].sudo().browse(partner_id)
        if user_rec:
            partner_id = user_rec.id
            domain = [('partner_id', '=', partner_id)]
        else:
            # TO DO
            result.update({'message': 'Customer not available with id ' + str(partner_id), 'result': False})
        if date:
            st_time = date + ' 00:00:00'
            en_time = date + ' 23:59:59'
            st_dt = dt.strptime(st_time, DEFAULT_SERVER_DATETIME_FORMAT)
            en_dt = dt.strptime(en_time, DEFAULT_SERVER_DATETIME_FORMAT)
            local = pytz.timezone(request.env.context.get('tz'))
            local_st_dt = local.localize(st_dt, is_dst=None)
            utc_st_dt = local_st_dt.astimezone(pytz.utc)
            local_en_dt = local.localize(en_dt, is_dst=None)
            utc_en_dt = local_en_dt.astimezone(pytz.utc)
            domain += [('date_order', '>=', local_st_dt),
                       ('date_order', '<=', local_en_dt),
                       ('state', '!=', 'cancel')]
        fields = ['id', 'name', 'partner_id', 'route_id', 'date_order', 'amount_total', 'order_line', 'state']
        sale_data = request.env['sale.order'].sudo().search_read(domain,
                                                          fields=fields, offset=[],
                                                          order='date_order desc')
        print ("sale_data", sale_data)
        for orders in sale_data:
            order_partner = orders.get('partner_id')
            partner = request.env['res.partner'].sudo().browse([order_partner[0]])
            partner_latitude = partner.partner_latitude
            partner_longitude = partner.partner_longitude
            order_amount = orders.get('amount_total')
            order = request.env['sale.order'].sudo().browse([orders.get('id')])
            order_amountremaining_amount = 0.0
            payment_amount = 0.0
            remaining_amount = 0.0
            message = ''
            for payment in order.invoice_ids:
                if payment.amount_residual > 0 and payment.state == 'posted':
                    message = "Partial Paid"
                    payment_amount = order_amount - payment.amount_residual
                    remaining_amount = payment.amount_residual
                if payment.amount_residual == 0 and payment.state == 'posted':
                    message = "Paid"
                    payment_amount = order_amount
                    remaining_amount = 0
                if payment.state == 'draft':
                    message = "Not Paid"
            orders.update({'Order Amount': order_amount, 'Payment Amount': payment_amount, 'Remaining Payment': remaining_amount,
                           'Payment Status': message, 'Partner Latitude': partner_latitude, 'Partner Longitude': partner_longitude})
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for records in sale_data:
            custom_array = []
            for line_id in request.env['sale.order.line'].sudo().browse(records["order_line"]):
                custom_array.append({'product_id': line_id.product_id.id,
                                     'name': line_id.product_id.name,
                                     'quantity': line_id.product_uom_qty,
                                     'price_subtotal': line_id.price_subtotal,
                                     'image': base_url + "/web/image?model=product.product&id=" + 
                                              str(line_id.product_id.id) + "&field=image_128"})
            records["order_line"] = custom_array
        return sale_data

    @validate_token
    @http.route('/GetOrdersByuser', type='json', auth='user')
    def get_sale_orders_by_user(self, user_id, date=False):
        domain = [('user_id', '=', user_id)]
        if date:
            st_time = date + ' 00:00:00'
            en_time = date + ' 23:59:59'
            st_dt = dt.strptime(st_time, DEFAULT_SERVER_DATETIME_FORMAT)
            en_dt = dt.strptime(en_time, DEFAULT_SERVER_DATETIME_FORMAT)
            local = pytz.timezone(request.env.context.get('tz'))
            local_st_dt = local.localize(st_dt, is_dst=None)
            utc_st_dt = local_st_dt.astimezone(pytz.utc)
            local_en_dt = local.localize(en_dt, is_dst=None)
            utc_en_dt = local_en_dt.astimezone(pytz.utc)
            domain += [('date_order', '>=', local_st_dt),
                       ('date_order', '<=', local_en_dt),
                       ('state', '!=', 'cancel')]
        fields = ['id', 'name', 'partner_id', 'route_id', 'date_order', 'amount_total', 'order_line']
        sale_data = request.env['sale.order'].search_read(domain,
                                                          fields=fields, offset=[],
                                                          order='date_order desc')
        for orders in sale_data:
            order_partner = orders.get('partner_id')
            partner = request.env['res.partner'].browse([order_partner[0]])
            partner_latitude = partner.partner_latitude
            partner_longitude = partner.partner_longitude
            order_amount = orders.get('amount_total')
            order = request.env['sale.order'].browse([orders.get('id')])
            remaining_amount = 0.0
            for payment in order.invoice_ids:
                remaining_amount += payment.amount_residual
            payment_amount = order_amount - remaining_amount
            if order_amount == payment_amount:
                message = "Paid"
            else:
                message = "Partial Paid"
            orders.update({'Order Amount': order_amount, 'Payment Amount': payment_amount, 'Remaining Payment': remaining_amount,
                           'Payment Status': message, 'Partner Latitude': partner_latitude, 'Partner Longitude': partner_longitude})
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for records in sale_data:
            custom_array = []
            for line_id in request.env['sale.order.line'].browse(records["order_line"]):
                custom_array.append({'product_id': line_id.product_id.id,
                                     'name': line_id.product_id.name,
                                     'quantity': line_id.product_uom_qty,
                                     'price_subtotal': line_id.price_subtotal,
                                     'image': base_url + "/web/image?model=product.product&id=" + 
                                              str(line_id.product_id.id) + "&field=image_128"})
            records["order_line"] = custom_array
        return sale_data

    @validate_token
    @http.route('/GetAssignedRoutes', type='json', auth='user')
    def get_assigned_routes(self, user_id):
        fields = ['route_ids']
        sales_rep = request.env['res.users'].search_read([('id', '=', user_id)], fields=fields, offset=[], order='id')
        route_list = []
        for records in sales_rep:
            for ids in records['route_ids']:
                routes = request.env['stock.warehouse'].browse(ids)
                route_list.append({"id": routes.id, "Route": routes.name})
            records['route_ids'] = route_list
        return route_list
    
    # TO TEST for ecommerce
    # @validate_token
    # @http.route('/CreateSaleOrderss', type='json', auth='user', cors='*', csrf=False)
    # def create_sale_orderss(self, partner_id, date_order, route_id, order_amount, order_details, user_id):
    #     sale_obj = request.env['sale.order']
    #     print ("order_details", order_details)
    #     # order_details = json.loads(order_details)
    #     # partner_id = user_id
    #     user_rec = request.env['res.users'].sudo().browse(partner_id)
    #     if user_rec:
    #         partner_id = user_rec.partner_id.id
    #     else:
    #         result.update({'message': 'Customer not available with id ' + str(partner_id), 'result': False})
    #     sale_line = []
    #     result = {}
    #     for line in order_details:
    #         test = request.env['product.product'].sudo().browse([int(line['product_id'])])
    #         if test.active:
    #             sale_line.append((0, 0, {
    #                 'product_id': int(line['product_id']),
    #                 'product_uom_qty': float(line['product_uom_qty']),
    #                 'price_subtotal': float(line['price_subtotal'])
    #             }))
    #         else:
    #             result.update({'message': str(test.id) + ' This product is Inactive, Please choose an Active Product',
    #                            'result': False})
    #             return result
    #     try:
    #         warehouse = request.env.ref('stock.warehouse0')
    #         sale_order = sale_obj.sudo().create({
    #             'partner_id': partner_id,
    #             'user_id': user_id,
    #             'route_id': route_id,
    #             'warehouse_id': warehouse.id,
    #             'date_order': date_order,
    #             'amount_total': order_amount,
    #             'order_line': sale_line,
    #             'payment_term_id': 1,
    #         })
    #         if sale_order:
    #             result.update({'message': 'Successfully Created Order ' + sale_order.name, 'result': True})
    #             result.update({"saleorder_id": sale_order.id, "user_id": sale_order.create_uid.id})
    #             return result
    #     except Exception as e:
    #         result.update({'message': e, 'result': False})
    #         return result

    # for ecommerce
    # @validate_token
    @http.route('/CreateSaleOrders', type='json', auth='public', cors='*')
    def create_sale_orders(self, partner_id, date_order, route_id, order_amount, order_details, user_id):
        sale_obj = request.env['sale.order']
        # order_details = json.loads(order_details)
        user_rec = request.env['res.users'].sudo().browse(partner_id)
        if user_rec:
            partner_id = user_rec.id
        else:
            result.update({'message': 'Customer not available with id ' + str(partner_id), 'result': False})
        sale_line = []
        result = {}
        for line in order_details:
            test = request.env['product.product'].sudo().browse([int(line['product_id'])])
            if test.active:
                sale_line.append((0, 0, {
                    'product_id': int(line['product_id']),
                    'product_uom_qty': float(line['product_uom_qty']),
                    'price_subtotal': float(line['price_subtotal'])
                }))
            else:
                result.update({'message': str(test.id) + ' This product is Inactive, Please choose an Active Product',
                               'result': False})
                return result
        try:
            warehouse = request.env.ref('stock.warehouse0')
            sale_order = sale_obj.sudo().create({
                'partner_id': partner_id,
                'user_id': user_id,
                'route_id': route_id,
                'warehouse_id': warehouse.id,
                'date_order': date_order,
                'amount_total': order_amount,
                'order_line': sale_line,
                'payment_term_id': 1,
            })
            if sale_order:
                result.update({'message': 'Successfully Created Order ' + sale_order.name, 'result': True})
                result.update({"saleorder_id": sale_order.id, "user_id": sale_order.create_uid.id})
        except Exception as e:
            result.update({'message': e, 'result': False})
            return result
        return result

    @validate_token
    @http.route('/CreateSaleOrder', type='json', auth='user')
    def create_sale_order(self, partner_id, date_order, route_id, order_amount, order_details, user_id):
        sale_obj = request.env['sale.order']
        sale_line = []
        result = {}
        for line in order_details:
            test = request.env['product.product'].browse([int(line['product_id'])])
            if test.active:
                sale_line.append((0, 0, {
                    'product_id': int(line['product_id']),
                    'product_uom_qty': float(line['product_uom_qty']),
                    'price_subtotal': float(line['price_subtotal'])
                }))
            else:
                result.update({'message': str(test.id) + ' This product is Inactive, Please choose an Active Product',
                               'result': False})
                return result
        try:
            warehouse = request.env.ref('stock.warehouse0')
            sale_order = sale_obj.sudo().create({
                'partner_id': partner_id,
                'user_id': user_id,
                'route_id': route_id,
                'warehouse_id': warehouse.id,
                'date_order': date_order,
                'amount_total': order_amount,
                'order_line': sale_line,
                'payment_term_id': 1,
            })

        except Exception as e:
            result.update({'message': e, 'result': False})
            return result
        if sale_order:
            result.update({'message': 'Successfully Created Order ' + sale_order.name, 'result': True})
        result.update({"saleorder_id": sale_order.id, "user_id": sale_order.create_uid.id})
        return result

    @validate_token
    @http.route('/FulfillSaleOrder', type='json', auth='user')
    def fulfil_sale_order(self, sale_id, journal_id, vehicle_id, driver_id, payment_reference, payment_amount):
        result = {}
        print ("payment amount", payment_amount)
        # Check SaleOrder if already fulfilled.
        sale_obj = request.env['sale.order'].sudo().browse(sale_id)
        if sale_obj.state in ('sale', 'done'):
            picking = sale_obj.picking_ids.filtered(lambda r: r.state not in ('cancel', 'done'))
            if not picking.ids:
                result.update({'message': "Sale Order : " + sale_obj.name + ' already fulfilled', 'result': True})
                sale_obj.write({'sale_status': 'fulfill'})
                return result
        vehicle_rec = request.env["fleet.vehicle"].search([('id', '=', vehicle_id)])
        # recon_obj = request.env['account.reconciliation.widget']
        try:
            if sale_obj.state == 'cancel':
                result.update({'message': "Sale Order : " + sale_obj.name + ' is cancelled', 'result': False})
                return result
            if sale_obj.state == 'done':
                sale_obj.action_unlock()
            if sale_obj.state == 'sale':
                sale_obj.action_cancel()
                sale_obj.action_draft()
            driver = request.env['res.users'].search([('id', '=', driver_id)])
            sale_vals = {
                'vehicle_id': vehicle_id,
            }
            if vehicle_rec.warehouse_id:
                sale_vals.update({
                    'warehouse_id': vehicle_rec.warehouse_id.id
                })
            sale_obj.sudo()._onchange_vehicle()
            sale_obj.sudo().write(sale_vals)
            sale_obj.action_confirm()
            sale_order = sale_obj
            stock_location = request.env['stock.location'].search([("id", "=", sale_obj.warehouse_id.lot_stock_id.id)])
            precision_digits = request.env['decimal.precision'].precision_get('Product Unit of Measure')
            for picking in sale_order.picking_ids.filtered(lambda r: r.state not in ('cancel', 'done', 'draft')):
                moves = picking.mapped('move_lines').filtered(
                    lambda move: move.state not in ('draft', 'cancel', 'done'))
                if moves:
                    picking.do_unreserve()
                product_name = ''
                for stock in picking.move_ids_without_package:
                    stock_quant = request.env['stock.quant'].search(
                    [("location_id", "=", stock_location.id),
                     ('product_id', '=', stock.product_id.id)])
                    if not stock_quant:
                        product_name += stock.product_id.name_get()[0][1] + ', '
                    if stock_quant:
                        toatl_qty = 0
                        for quant in stock_quant:
                            toatl_qty += quant.available_quantity
                        if toatl_qty < stock.product_uom_qty:
                            product_name += stock.product_id.name_get()[0][1] + ', '
                if product_name:
                    result.update(
                    {'message': "Insufficient Stock Please Update Your Stock for products " + product_name,
                     'result': False})
                if result:
                    # cancel the order to unreserve qty
                    sale_obj.action_cancel()
                    sale_obj.action_draft()
                    return result
#                 moves = picking.mapped('move_lines').filtered(
#                     lambda move: move.state not in ('draft', 'cancel', 'done'))
                if moves:
                    # reserve qty and validate
                    picking.action_assign()
                    picking.button_validate()
                no_quantities_done = all(
                    float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                    picking.move_line_ids.filtered(
                        lambda m: m.state not in ('done', 'cancel')))
                if no_quantities_done:
                    wiz = request.env['stock.immediate.transfer'].create(
                        {'show_transfers': True, 'pick_ids': [(4, picking.id)]})
                    request.env['stock.immediate.transfer.line'].create(
                        {'to_immediate': True, 'picking_id': picking.id, 'immediate_transfer_id': wiz.id})
                    wiz.with_context(button_validate_picking_ids=picking.id).process()
            customer_invoice = sale_order.sudo()._create_invoices()
            customer_invoice.sudo().action_post()
            if not payment_amount:
                payment_amount = customer_invoice.amount_total
            inv_move_line = customer_invoice.line_ids.filtered(
                lambda r: r.account_id == customer_invoice.partner_id.property_account_receivable_id)
            print ("inv_move_line", inv_move_line)
            method = request.env['account.payment.method'].sudo().search([('code', '=', 'manual')], limit=1)
            journal = request.env['account.journal'].browse(journal_id)
            if journal.mpesa_reconciliation == True:
                payment = request.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': customer_invoice.name,
                    'journal_id': journal_id,
                    'pay_ref': payment_reference,
                    'line_ids': [(0, 0, {"account_id": customer_invoice.partner_id.property_account_receivable_id.id,
                                         "partner_id": customer_invoice.partner_id.id,
                                         "credit": float(payment_amount)}),
                                 (0, 0, {"account_id": journal.default_account_id.id,
                                         "partner_id": driver.partner_id.id,
                                         "debit": float(payment_amount)})]
                })
            else:
                payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'pay_ref': payment_reference,
                    'partner_id': customer_invoice.partner_id.id,
                    'ref': customer_invoice.name,
                    'journal_id': journal_id,
                    'amount': payment_amount,
                    'currency_id': customer_invoice.currency_id.id,
                    'payment_method_id': method.id,
                    'partner_bank_id': customer_invoice.partner_bank_id.id,
                    'destination_account_id': customer_invoice.partner_id.property_account_receivable_id.id,
                })
            payment.sudo().action_post()
            pay_move_line = payment.line_ids.filtered(
                lambda r: r.account_id == customer_invoice.partner_id.property_account_receivable_id)
            move_line_ids = (inv_move_line + pay_move_line).ids
            # recon_obj.sudo()._process_move_lines(move_line_ids, [])
            result.update({'message': "Successfully fulfilled Order " + sale_obj.name, 'result': True})
            return result
        except Exception as e:
            result.update({'message': e, 'result': False})
            return result

    @validate_token
    @http.route('/UpdateSaleOrder', type='json', auth='user')
    def update_sale_order(self, saleorder_id, driver_id, order_details):
        saleorder = request.env['sale.order'].search([('id', '=', saleorder_id)])
        if saleorder.state == 'done':
            saleorder.action_unlock()
        saleorder.action_cancel()
        saleorder.action_draft()
        sale_line = []
        result = {}
        user_obj = request.env['res.users']
        for line in order_details:
            test = request.env['product.product'].browse([int(line['product_id'])])
            if test.active:
                sale_line.append((0, 0, {
                    'product_id': int(line['product_id']),
                    'product_uom_qty': float(line['product_uom_qty'])
                }))
            else:
                result.update({'message': test.name + ' This product is Inactive, Please choose an Active Product',
                               'result': False})
                return result
        if saleorder.order_line:
            saleorder.order_line.unlink()
        try:
            user = user_obj.browse(driver_id)
            saleorder.write({
                'driver_id': user.partner_id.id,
                'order_line': sale_line})
            saleorder.action_confirm()
        except Exception as e:
            result.update({"message": e, 'result': False})
            return result
        else:
            result.update(
                {"message": "Successfully Updated Order " + saleorder.name, 'saleorder': saleorder.id, 'result': True})
        return result

    @validate_token
    @http.route('/PaySaleOrder', type='json', auth='user')
    def pay_sale_order(self, sale_id, journal_id, driver_id, payment_reference, payment_amount=0.0):
        # TODO: Need to create a payment with the amount passed and reconcile it against the invoice of the Sale Order
        result = {}
        sale_order = request.env['sale.order'].browse(sale_id)
        driver = request.env['res.users'].search([('id', '=', driver_id)])
        if sale_order.invoice_ids.id != False:
            customer_invoice = request.env['account.move'].browse(sale_order.invoice_ids.id)
            # recon_obj = request.env['account.reconciliation.widget']
            inv_move_line = customer_invoice.line_ids.filtered(
                lambda r: r.account_id == customer_invoice.partner_id.property_account_receivable_id)
            method = request.env['account.payment.method'].search([('code', '=', 'manual')], limit=1)
            journal = request.env['account.journal'].browse(journal_id)
            if journal.mpesa_reconciliation == True:
                payment = request.env['account.move'].sudo().create({
                    'move_type': 'entry',
                    'ref': customer_invoice.name,
                    'journal_id': journal_id,
                    'pay_ref': payment_reference,
                    'line_ids': [(0, 0, {"account_id": customer_invoice.partner_id.property_account_receivable_id.id,
                                         "partner_id": customer_invoice.partner_id.id,
                                         "credit": float(payment_amount)}),
                                 (0, 0, {"account_id": journal.default_account_id.id,
                                         "partner_id": driver.partner_id.id,
                                         "debit": float(payment_amount)})]
                })
            else:
                payment = request.env['account.payment'].sudo().create({
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'pay_ref': payment_reference,
                    'partner_id': customer_invoice.partner_id.id,
                    'ref': customer_invoice.name,
                    'journal_id': journal_id,
                    'amount': float(payment_amount),
                    'currency_id': customer_invoice.currency_id.id,
                    'payment_method_id': method.id,
                    'partner_bank_id': customer_invoice.partner_bank_id.id,
                    'destination_account_id': customer_invoice.partner_id.property_account_receivable_id.id,
                })
            payment.action_post()
            pay_move_line = payment.line_ids.filtered(
                lambda r: r.account_id == customer_invoice.partner_id.property_account_receivable_id)
            move_line_ids = (inv_move_line + pay_move_line).ids
            # recon_obj.sudo()._process_move_lines(move_line_ids, [])
            result.update({'message': "Successfully Payment " + sale_order.name + " Order", 'result': True})
        else:
            result.update({"message": sale_order.name + " Order is not fulfill Order, Please Fulfill", 'sale order': sale_order.id, 'result': False})
        return result

    @validate_token
    @http.route('/GetProductPriceByRoute', type='json', auth='user')
    def get_product_price_by_route(self, customer_id, route_id):
        fields = ['id', 'name', 'list_price', 'image_128']
        customer = request.env['res.partner'].browse(customer_id)
        customer_pl = customer.property_product_pricelist
        if not customer_pl.ids:
            customer_pl = request.env['product.pricelist'].search([
                ('route_id', '=', route_id),
                ('name','=','Public Pricelist'),
                ('customer_type_id', '=', customer.customer_type_id.id)], limit=1)
        product_obj = request.env["product.product"]
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        product_template_main = product_obj.search_read([('type', '=', 'product')], fields=fields, order='id')
        for product_rec in product_template_main:
            product_price = product_obj.browse(product_rec.get('id')).with_context(pricelist=customer_pl.id).lst_price
            product_rec.update({"pricelist_price": product_price})
            product_rec['image_128'] = base_url + "/web/image?model=product.product&id=" + str(
                product_rec['id']) + "&field=image_128"
        return product_template_main

    @http.route('/GetProducts', type='json', auth='public', cors='*')
    def get_products(self,):
        # api for guest users
        fields = ['id', 'name', 'list_price', 'image_128', 'categ_id', 'default_code', 'uom_id']
        customer_pl = request.env['product.pricelist'].sudo().search([('name', '=', 'E-commerce')], limit=1)
        product_obj = request.env["product.product"]
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        product_template_main = product_obj.sudo().search_read([('type', '=', 'product'), ('sale_ok', '=', True)], fields=fields, order='id')
        stock_location = request.env.ref('stock.stock_location_stock')
        for product_rec in product_template_main:
            stock_quant = request.env['stock.quant'].sudo().search([("location_id", "=", stock_location.id), ('product_id','=',product_rec.get('id'))])
            qty_total = 0
            for sq in stock_quant:
                qty_total += sq.quantity
            product_price = product_obj.sudo().browse(product_rec.get('id')).with_context(pricelist=customer_pl.id).lst_price
            product_rec.update({"pricelist_price": product_rec.get('list_price')})
            product_rec.update({"Available Quantity": qty_total})
            product_rec.update({'Price': product_price})
            product_rec.update({'SKU': product_rec.get('uom_id')[1]})
            product_rec.update({'CategoryID': product_rec.get('categ_id')[0]})
            product_rec.update({'CategoryName': product_rec.get('categ_id')[1]})
            product_rec['Image'] = base_url + "/web/image?model=product.product&id=" + str(
                product_rec['id']) + "&field=image_128"
            del product_rec['categ_id']
            del product_rec['list_price']
            del product_rec['image_128']
            del product_rec['uom_id']
        return product_template_main

    @validate_token
    @http.route('/GetWarehouses', type='json', auth='user')
    def get_warehouse(self):
        fields = ['id', 'name']
        warehouse_data = request.env['stock.warehouse'].search_read([],
                                                                    fields=fields, offset=[],
                                                                    order='id')
        return warehouse_data

    @validate_token
    @http.route('/GetVehicle', type='json', auth='user')
    def get_vehicle(self):
        fields = ['id', 'name']
        vehicle_data = request.env['stock.warehouse'].search_read([('vehicle', '=', True)],
                                                                    fields=fields, offset=[],
                                                                    order='id')
        return vehicle_data

    @validate_token
    @http.route('/GetCustomerTypes', type='json', auth='user')
    def get_customer_types(self):
        customer_types = request.env['customer.type'].search_read([], fields=['id', 'customer_type'], offset=[],
                                                                  order='id')
        return customer_types

    @validate_token
    @http.route('/CancelSaleOrder', type='json', auth='user')
    def cancel_sale_order(self, sale_order_id):
        sale_order = request.env['sale.order'].search([('id', '=', sale_order_id)])
        sale_order.action_unlock()
        delivery = sale_order.picking_ids
        if delivery.state == 'sale':
            return {'result': True,
                    'message': ('Error: Your order was delivered, So cannot be cancelled.'),
                    }
        else:
            sale_order.action_cancel()
            return {'result': False,
                    'message': ('Your order is Cancelled successfully.'),
                    }

    @http.route('/GetEcommerceRoutes', type='json', auth='public', cors='*', csrf=False)
    def get_ecommerce_routes(self):
        fields = ['id', 'name']
        result = {}
        try:
            route_data = request.env['stock.warehouse'].sudo().search_read([('route', '=', True)],
                                                                    fields=fields,
                                                                    offset=[],
                                                                    order='id')
            print ("route_data", route_data)
            return route_data
        except Exception as e:
            result.update({"message": e, 'result': False})
            return result

    @validate_token
    @http.route('/GetCustomerBalance', type='json', auth='user', csrf=False)
    def get_customer_balance(self, partner_id):
        contact = request.env['res.partner'].sudo().browse(int(partner_id))
        amount = abs(contact.total_due)
        return str({'result': True,
                'Customer': contact.name,
                'Total Due': str(amount),
                })
