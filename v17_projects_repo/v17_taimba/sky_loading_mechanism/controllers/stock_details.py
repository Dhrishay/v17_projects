# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import http, fields
from odoo.http import Response, request
from odoo.addons.sky_base_api.common import invalid_response, valid_response
import functools
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from datetime import date as dt
import calendar
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
        request.env = access_token_data.env(user=access_token_data.user_id)
        request.update_env(user=access_token_data.user_id)

        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class StockDetails(http.Controller):

    @validate_token
    @http.route('/PostLoadingOrder', type='json', auth='user')
    def post_loading_order(self, vehicle_id, date, order_details):
        result = {}
        try:
            vehicle_rec = request.env['fleet.vehicle'].browse(vehicle_id)
            loading_obj = request.env['stock.loading'].search([('type', '=', 'loading')])
            loading_line = []
            order_details_list = [order_details]
            for line in order_details:
                test = request.env['product.product'].browse([int(line['product_id'])])
                if test.active:
                    loading_line.append((0, 0, {
                        'product_id': int(line['product_id']),
                        'quantity': int(line['quantity']),
                        'lot_id': int(line['lot_id']) if line['lot_id'] else False
                    }))
                else:
                    result.update(
                        {'message': str(test.id) + ' This product is Inactive, Please choose an Active Product',
                         'result': False})
                    return result

            loading_order = loading_obj.sudo().create({
                'driver_id': vehicle_rec.driver_id.id,
                'vehicle_id': vehicle_id,
                'type': 'loading',
                'post_true': True,
                'date': date,
                'stock_loading_unloading_lines': loading_line
            })
            warehouse = request.env.ref('stock.warehouse0').id
            if loading_order.type == "loading":
                loading_order.update({"source_warehouse_id": warehouse})
            if loading_order.type == "unloading":
                loading_order.update({"destination_warehouse_id": warehouse})
            loading_order.onchange_vehicle()
            loading_order.confirm_mechanism()
            if loading_order:
                result.update({"message": "Loading Successfully Created " + str(loading_order.sequence_id)})
        except Exception as e:
            result.update({'message': e})
            return result
        return result

    @validate_token
    @http.route('/PostUnloadingOrder', type='json', auth='user')
    def post_unloading_order(self, vehicle_id, driver_id, date):
        result = {}
        try:
            unloading_obj = request.env['stock.loading'].search([('type', '=', 'unloading')])
            driver = request.env['res.users'].search([('id', '=', driver_id)])
            vehicle = request.env['fleet.vehicle'].search([('id', '=', vehicle_id)])
            if driver.ids and vehicle.ids:
                unloading_order = unloading_obj.sudo().create({
                    'driver_id': driver.partner_id.id,
                    'type': 'unloading',
                    'vehicle_id': vehicle_id,
                    'post_true': True,
                    'date': date,
                })
                warehouse = request.env.ref('stock.warehouse0').id
                if unloading_order.type == "loading":
                    unloading_order.update({"source_warehouse_id": warehouse})
                if unloading_order.type == "unloading":
                    unloading_order.update({"destination_warehouse_id": warehouse})
                unloading_order.onchange_vehicle()
                if unloading_order:
                    result.update({"message": "Unloading Successfully Created " ,
                                   'Order Id': str(unloading_order.id),
                                   'Order State': str(unloading_order.state),
                                   'result': True})
            else:
                if not driver.ids:
                    result.update({"message": "Driver not Existing!", 'result': False})
                elif not vehicle.ids:
                    result.update({"message": "Vehicle not Existing!", 'result': False})
        except Exception as e:
            result.update({'message': e, 'result': False})
            return result
        return result

    @validate_token
    @http.route('/GetLoadingOrder', type='json', auth='user')
    def get_loading_orders(self, date=False):
        if not date:
            date = dt.today()
            date = date.strftime('%Y-%m-%d')
        date_time = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        st_time = date_time.strftime('%Y-%m-%d') + ' 00:00:00'
        en_time = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        st_dt = datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S')
        en_dt = datetime.strptime(en_time, '%Y-%m-%d %H:%M:%S')
        # to convert the date from user timezone to UTC
        local = pytz.timezone(request.env.context.get('tz'))
        local_st_dt = local.localize(st_dt, is_dst=None)
        utc_st_dt = local_st_dt.astimezone(pytz.utc)
        local_en_dt = local.localize(en_dt, is_dst=None)
        utc_en_dt = local_en_dt.astimezone(pytz.utc)
        fields = ['vehicle_id', 'driver_id', 'date', 'handshaketoken', 'stock_loading_unloading_lines']
        stock_data = request.env['stock.loading'].search_read([("type", "=", "loading"), ("date", ">=", utc_st_dt),
                                                               ("date", "<=", utc_en_dt)],
                                                              fields=fields, offset=[],
                                                              order='id')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for records in stock_data:
            loading_line = []
            for line_id in request.env['stock.loading.lines'].browse(records["stock_loading_unloading_lines"]):
                loading_line.append({'product_id': line_id.product_id.id,
                                     'name': line_id.product_id.name,
                                     'quantity': line_id.quantity,
                                     'image' : base_url + "/web/image?model=product.product&id=" + 
                                             str(line_id.product_id.id) + "&field=image_128"})
            records["stock_loading_unloading_lines"] = loading_line
        return stock_data

    @validate_token
    @http.route('/GetUnloadingOrder', type='json', auth='user')
    def get_unloading_orders(self, date=False):
        if not date:
            date = dt.today()
            date = date.strftime('%Y-%m-%d')
        date_time = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        st_time = date_time.strftime('%Y-%m-%d') + ' 00:00:00'
        en_time = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        st_dt = datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S')
        en_dt = datetime.strptime(en_time, '%Y-%m-%d %H:%M:%S')
        # to convert the date from user timezone to UTC
        local = pytz.timezone(request.env.context.get('tz'))
        local_st_dt = local.localize(st_dt, is_dst=None)
        utc_st_dt = local_st_dt.astimezone(pytz.utc)
        local_en_dt = local.localize(en_dt, is_dst=None)
        utc_en_dt = local_en_dt.astimezone(pytz.utc)
        fields = ['vehicle_id', 'driver_id', 'date', 'handshaketoken', 'stock_loading_unloading_lines']
        stock_data = request.env['stock.loading'].search_read([("type", "=", "unloading"), ("date", ">=", utc_st_dt),
                                                               ("date", "<=", utc_en_dt)],
                                                              fields=fields, offset=[],
                                                              order='id')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for records in stock_data:
            unloading_line = []
            for line_id in request.env['stock.loading.lines'].browse(records["stock_loading_unloading_lines"]):
                unloading_line.append({'product_id': line_id.product_id.id,
                                       'name': line_id.product_id.name,
                                       'quantity': line_id.quantity,
                                       'image': base_url + "/web/image?model=product.product&id=" + 
                                                str(line_id.product_id.id) + "&field=image_128"
                                       })
            records["stock_loading_unloading_lines"] = unloading_line
        return stock_data

    @validate_token
    @http.route('/GetAssignedVehicle', type='json', auth='user')
    def get_assigned_vehicle(self, user_id):
        user_id = request.env['res.users'].browse(user_id)
        vehicle_assigned = request.env['fleet.vehicle'].search([("driver_id", "=", user_id.partner_id.id)], limit=1)
        custom_dict = {}
        for record in vehicle_assigned:
            custom_dict.update({"id": record.id, "name": record.display_name})
        return custom_dict

    @validate_token
    @http.route('/GetVehicleLoading', type='json', auth='user')
    def get_vehicle_loading(self, vehicle_id, date=False):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not date:
            date = dt.today()
            date = date.strftime('%Y-%m-%d')
        date_time = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        st_time = date_time.strftime('%Y-%m-%d') + ' 00:00:00'
        en_time = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        st_dt = datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S')
        en_dt = datetime.strptime(en_time, '%Y-%m-%d %H:%M:%S')
        # to convert the date from user timezone to UTC
        local = pytz.timezone(request.env.context.get('tz'))
        local_st_dt = local.localize(st_dt, is_dst=None)
        utc_st_dt = local_st_dt.astimezone(pytz.utc)
        local_en_dt = local.localize(en_dt, is_dst=None)
        utc_en_dt = local_en_dt.astimezone(pytz.utc)
        fields = ['date', 'source_warehouse_id', 'stock_loading_unloading_lines']
        vehicle_loading = request.env['stock.loading'].search_read([
            ("vehicle_id", "=", vehicle_id),
            ("date", ">=", utc_st_dt),
            ('date', '<=', utc_en_dt),
            ("type", "=", "loading")],
            fields=fields, offset=[],
            order='id')
        vehicle = request.env['fleet.vehicle'].search([('id', '=', vehicle_id)])
        stock_location = request.env['stock.location'].search([("id", "=", vehicle.warehouse_id.lot_stock_id.id)])
        for records in vehicle_loading:
            custom_array = []
            for line_id in request.env['stock.loading.lines'].browse(records["stock_loading_unloading_lines"]):
                stock_quant = request.env['stock.quant'].search(
                    [("location_id", "=", stock_location.id),('product_id','=',line_id.product_id.id)])
                stock_quant_total = 0.0
                stock_quant_total += sum([quant.available_quantity for quant in stock_quant])
                custom_array.append({
                    'product_id': line_id.product_id.id,
                    'product_name': line_id.product_id.name,
                    'current_stock': stock_quant_total,
                    'quantity': line_id.quantity,
                    'image': base_url + "/web/image?model=product.product&id=" + 
                                             str(line_id.product_id.id) + "&field=image_128"})
            records["stock_loading_unloading_lines"] = custom_array
            stock_loading_lines = records["stock_loading_unloading_lines"]
            del records["stock_loading_unloading_lines"]
            records.update({"stock_loading_lines": stock_loading_lines})
        return vehicle_loading

    @validate_token
    @http.route('/GetRouteOrder', type='json', auth='user')
    def get_route_order(self, route_id):

        fields = ['name', 'partner_id', 'date_order', 'amount_total', 'route_id', 'order_line']

        route_order = request.env['sale.order'].search_read([("route_id", "=", route_id)],
                                                            fields=fields, offset=[],
                                                            order='date_order desc')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for records in route_order:

            phone_number = request.env['res.partner'].browse(records['partner_id'][0])

            order_lines = []
            for line_id in request.env['sale.order.line'].browse(records["order_line"]):
                order_lines.append({'product_id': line_id.product_id.id,
                                    'name': line_id.product_id.name,
                                    'quantity': line_id.product_uom_qty,
                                    'price_subtotal': line_id.price_subtotal,
                                    'image': base_url + "/web/image?model=product.product&id=" + 
                                             str(line_id.product_id.id) + "&field=image_128"
                                    })
            records["order_line"] = order_lines
            records.update({"phone_number": [phone_number.phone]})
        return route_order

    @validate_token
    @http.route('/PostOrderDriver', type='json', auth='user')
    def post_order_driver(self, driver_id, vehicle_id, partner_id, date_order, route_id, order_amount, order_details):
        result = {}
        sale_obj = request.env['sale.order']
        sake_line = []
        for line in order_details:
            test = request.env['product.product'].browse([int(line['product_id'])])
            if test.active:
                sake_line.append((0, 0, {
                    'product_id': int(line['product_id']),
                    'product_uom_qty': int(line['product_uom_qty']),
                    'price_subtotal': int(line['price_subtotal'])
                }))
            else:
                result.update({'message': str(test.id) + ' This product is Inactive, Please choose an Active Product',
                               'result': False})
                return result

            driver_order = sale_obj.sudo().create({
                'driver_id': driver_id,
                'vehicle_id': vehicle_id,
                'partner_id': partner_id,
                'warehouse_id': route_id,
                'date_order': date_order,
                'amount_total': order_amount,
                'order_line': sake_line
            })
            driver_order.action_confirm()
        if driver_order:
            result.update({'message': 'Successfully Created Order ' + driver_order.name, 'result': True})
        result.update({"saleorder_id": driver_order.id, "user_id": driver_order.create_uid.id})
        return result

    @validate_token
    @http.route('/GetVehilcleSalesDetailed', type='json', auth='user')
    def get_vehicle_sale_details(self, vehicle_id, date):
        if not date:
            date = dt.today()
            date = date.strftime('%Y-%m-%d')
        date_time = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        st_time = date_time.strftime('%Y-%m-%d') + ' 00:00:00'
        en_time = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        st_dt = datetime.strptime(st_time, '%Y-%m-%d %H:%M:%S')
        en_dt = datetime.strptime(en_time, '%Y-%m-%d %H:%M:%S')
        # to convert the date from user timezone to UTC
        local = pytz.timezone(request.env.context.get('tz'))
        local_st_dt = local.localize(st_dt, is_dst=None)
        utc_st_dt = local_st_dt.astimezone(pytz.utc)
        local_en_dt = local.localize(en_dt, is_dst=None)
        utc_en_dt = local_en_dt.astimezone(pytz.utc)

        fields = ['partner_id', 'amount_total', 'state', 'order_line']
        field1 = ['journal_id', 'state', 'amount']
        sale_order = request.env['sale.order'].search([('vehicle_id', '=', vehicle_id), ("date_order", ">=", utc_st_dt),
                                                       ('date_order', '<=', utc_en_dt), ])
        custom_array = []
        for sale in sale_order:
            sale_order_details = sale.search_read([('id', '=', sale.id)], fields=fields, offset=[], order='id')
            for records in sale_order_details:
                order = []
                for line_id in request.env['sale.order.line'].browse(records['order_line']):
                    order.append({'product_id': line_id.product_id.id,
                                  'product_name': line_id.product_id.name,
                                  'product_uom_qty': line_id.product_uom_qty})
                records["order_line"] = order
            custom_array.append(sale_order_details)
            for invoice in sale.invoice_ids:
                payment = request.env['account.payment'].search_read([('ref', '=', invoice.payment_reference)],
                                                                     fields=field1, offset=[], order='id')
                custom_array.append(payment)
        return custom_array

    @validate_token
    @http.route('/GetVehicleProductLot', type='json', auth='user')
    def get_vehicle_product_lot(self, vehicle_id, product_id):
        fields = ['lot_id', 'quantity']
        fleet = request.env['fleet.vehicle'].search([('id', '=', vehicle_id)])
        stock_quant = request.env['stock.quant'].search_read(
            [("location_id", "=", fleet.warehouse_id.lot_stock_id.id), ('product_id', '=', product_id)],
            fields=fields, offset=[], order='id')
        return stock_quant

    @validate_token
    @http.route('/GetProductLot', type='json', auth='user')
    def get_loading_product_lot(self, warehouse_id, product_id):
        fields = ['lot_id', 'quantity']
        warehouse = request.env['stock.warehouse'].search([('id', '=', warehouse_id)])
        stock_quant = request.env['stock.quant'].search_read(
            [("location_id", "=", warehouse.lot_stock_id.id), ('product_id', '=', product_id)],
            fields=fields, offset=[], order='id')
        return stock_quant

    @validate_token
    @http.route('/GetVehicleStockLevel', type='json', auth='user')
    def get_vehicle_stock_level(self, vehicle_id):
        product_ids = []
        product_array = []
        datas = []
        field = ['id', 'name']
        products = request.env['product.product'].search_read([], fields=field, offset=[], order='id')
        cr = request._cr
        query = "select product_id,sum(quantity) AS load from stock_loading_lines as r1 join stock_loading as t1 on t1.id=r1.stock_loading_id where t1.type='loading' and vehicle_id=" + str(
            vehicle_id) + " group by product_id"
        query1 = "select product_id,sum(quantity) AS sale from stock_move_line as r1 inner join stock_picking as t1 on t1.id=r1.picking_id , stock_picking_type st where t1.picking_type_id = st.id and st.code='outgoing' and vehicle_id=" + str(
            vehicle_id) + " group by product_id"
        query2 = "select product_id,sum(quantity) AS issues from stock_move_line as r1 inner join stock_picking as t1 on t1.id=r1.picking_id , stock_picking_type st where t1.picking_type_id = st.id and st.code='internal' and vehicle_id=" + str(
            vehicle_id) + " group by product_id"
        request._cr.execute(query)
        load_results = request._cr.dictfetchall()
        request._cr.execute(query1)
        delivery_results = request._cr.dictfetchall()
        request._cr.execute(query2)
        inter_results = request._cr.dictfetchall()
        product_array.append(load_results)
        product_array.append(delivery_results)
        product_array.append(inter_results)
        for product_id in products:
            product_ids.append(product_id)
        for id in product_ids:
            if id['id'] == id['id']:
                prod_data = []
                prod_data.append(id['id'])
                prod_data.append(id['name'])
            for produ_id in product_array[0]:
                if id['id'] == produ_id['product_id']:
                    prod_data.append('load')
                    prod_data.append(produ_id['load'])
            for produ_id in product_array[1]:
                if id['id'] == produ_id['product_id']:
                    prod_data.append('sale')
                    prod_data.append(produ_id['sale'])
            for produ_id in product_array[2]:
                if id['id'] == produ_id['product_id']:
                    prod_data.append('issues')
                    prod_data.append(produ_id['issues'])
            datas.append(prod_data)
        return datas

    @validate_token
    @http.route('/GetVehiclesSalesSummary', type='json', auth='user')
    def get_vehicle_sale_summary(self, vehicle_id):
        query = "select sum(quantity) AS load from stock_loading_lines as r1 join stock_loading as t1 on t1.id=r1.stock_loading_id where t1.type='loading' and vehicle_id=" + str(
            vehicle_id)
        query1 = "select sum(quantity) AS sale from stock_move_line as r1 inner join stock_picking as t1 on t1.id=r1.picking_id , stock_picking_type st where t1.picking_type_id = st.id and st.code='outgoing' and vehicle_id=" + str(
            vehicle_id)
        request._cr.execute(query)
        load_results = request._cr.dictfetchall()
        request._cr.execute(query1)
        delivery_results = request._cr.dictfetchall()
        for load in load_results:
            test = load['load']
        for delivery_value in delivery_results:
            test1 = delivery_value['sale']
        varience = test - test1
        total_varience = "['varience':{}]".format(varience)
        total_load = str(load_results).replace("{", "").replace("}", "")
        total_sale = str(delivery_results).replace("{", "").replace("}", "")
        return total_load, total_sale, total_varience

    @validate_token
    @http.route('/GetDashboard', type='json', auth='user')
    def get_dashboard_create(self, date, salesperson):
        dates = datetime.strptime(date, "%Y-%m-%d")
        start_date = dates.replace(day=1)
        new_date = calendar.monthrange(start_date.year, start_date.month)
        last_date = dates.replace(day=new_date[1])
        last_date = last_date.strftime('%Y-%m-%d') + ' 23:59:59'
        today_date = str(fields.Datetime.today())[:10]
        date_time = datetime.strptime(today_date, DEFAULT_SERVER_DATE_FORMAT)
        mtd_end_date = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        st_time = date_time.strftime('%Y-%m-%d') + ' 00:00:00'
        en_time = date_time.strftime('%Y-%m-%d') + ' 23:59:59'
        date_target = request.env['sales.target']
        date_target_temp = date_target.sudo().search([("user_id", "=", salesperson),
                                                      ("start_date", ">=", str(start_date)[:10]),
                                                      ('end_date', '<=', last_date[:10])],
                                              order='start_date desc', limit=1)
        sale_orders = request.env['sale.order'].sudo()
        orders = sale_orders.search([("user_id", "=", salesperson), ("date_order", ">=", str(start_date)),
                                     ('date_order', '<=', last_date), ('sale_status', '=', 'fulfill')])
        today_orders = sale_orders.search([("user_id", "=", salesperson), ("date_order", ">=", st_time),
                                           ("date_order", "<=", en_time), ('sale_status', '=', 'fulfill')])
        
        mtd_orders = sale_orders.search([("user_id", "=", salesperson), ("date_order", ">=", str(start_date)),
                                         ("date_order", "<=", mtd_end_date), ('sale_status', '=', 'fulfill')])
        today_sales = 0
        total_sales = 0
        total_mtd_sales = 0
        value_of_target = 0
        value_of_today_target = 0
        value_of_mtd_target = 0
        total_balance_value = {}
        for dt in date_target_temp:
            value_of_target += dt.total_target
            value_of_today_target += dt.daily_target
            value_of_mtd_target += dt.total_target
        for order in orders:
            total_sales += order.amount_total
        for order_today in today_orders:
            today_sales += order_today.amount_total
        for order_mtd in mtd_orders:
            total_mtd_sales += order_mtd.amount_total
        total_balance = value_of_target - total_sales
        today_balance = value_of_today_target - today_sales
        total_mtd_balance = value_of_target - total_sales
        total_balance_value.update(
            {'Total Target': value_of_target, 'Total Sales': total_sales, 'Total Balance': total_balance,
             'Today Target': value_of_today_target, 'Today Sales': today_sales, 'Today Balance': today_balance,
             'MTD Target': value_of_mtd_target, 'MTD Sales': total_mtd_sales, 'MTD Balance': total_mtd_balance})
        return total_balance_value

    @validate_token
    @http.route('/GetLoadingProducts', type='json', auth='user')
    def get_loading_product(self, vehicle_id, date=False):
        domain = [("type", "=", "loading"), ('vehicle_id', '=', vehicle_id)]
        if date:
            st_time = date + ' 00:00:00'
            en_time = date + ' 23:59:59'
            st_dt = datetime.strptime(st_time, DEFAULT_SERVER_DATETIME_FORMAT)
            en_dt = datetime.strptime(en_time, DEFAULT_SERVER_DATETIME_FORMAT)
            local = pytz.timezone(request.env.context.get('tz'))
            local_st_dt = local.localize(st_dt, is_dst=None)
            utc_st_dt = local_st_dt.astimezone(pytz.utc)
            local_en_dt = local.localize(en_dt, is_dst=None)
            utc_en_dt = local_en_dt.astimezone(pytz.utc)
            domain += [('date', '>=', utc_st_dt), ('date', '<=', utc_en_dt)]
        fields = ['stock_loading_unloading_lines']
        stock_data = request.env['stock.loading'].search_read(domain, fields=fields, order='id')
        dict_data = {}
        vehicle = request.env['fleet.vehicle'].search([('id', '=', vehicle_id)])
        stock_location = request.env['stock.location'].search([("id", "=", vehicle.warehouse_id.lot_stock_id.id)])
        for records in stock_data:
            for line_id in request.env['stock.loading.lines'].browse(records["stock_loading_unloading_lines"]):
                stock_quant = request.env['stock.quant'].search(
                    [("location_id", "=", stock_location.id),
                     ('product_id','=',line_id.product_id.id)])
                stock_quant_total = 0.0
                stock_quant_total += sum([quant.available_quantity for quant in stock_quant])
                if line_id.product_id.name not in dict_data:
                    dict_data.update({line_id.product_id.name: {
                                                                'Product ID': line_id.product_id.id,
                                                                'Product Name': line_id.product_id.name,
                                                                'Product Loading QTY': line_id.quantity,
                                                                'Product UOM': line_id.product_id.uom_id.name,
                                                                'Product Price': line_id.product_id.lst_price,
                                                                'Product Subtotal': line_id.product_id.lst_price * line_id.quantity,
                                                                'Current Stock': stock_quant_total,
                                                                'Current Subtotal' : round(line_id.product_id.lst_price * stock_quant_total, 2)
                                                                }})
                else:
                    qt = dict_data[line_id.product_id.name].get('Product Loading QTY')
                    qt_total = qt + line_id.quantity
                    for item in dict_data:
                        if item == line_id.product_id.name:
                            dict_data[item].update({'Product Loading QTY': qt_total,
                                                    'Current Stock': stock_quant_total,
                                                    'Current Subtotal' : round(line_id.product_id.lst_price * stock_quant_total, 2),
                                                    'Product Subtotal': line_id.product_id.lst_price * qt_total})
        list_data = []                   
        for key, val in dict_data.items():
            list_data.append(val)
        return list_data

