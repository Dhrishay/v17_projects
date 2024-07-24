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


class MpesaPayment(http.Controller):

    @validate_token
    @http.route('/PostMpesa', type='json', auth='user')
    def post_mpesa(self, sale_ids, salesrep_id, date, payment_amount, route_id, mpesa_ref, payment_method_id, cash_payment_method_id):
        account_move = request.env['account.move']
        result = {}
        try:
            mpesa_obj = request.env['mpesa.payment']
            gen_entry = []
            for sale in sale_ids:
                sale_data = request.env['sale.order'].browse(sale)
                invoice_data = account_move.browse(sale_data.invoice_ids.id)
                entry_data = account_move.search([('move_type', '=', 'entry'), ('ref', '=', invoice_data.name)])
                for entry in entry_data:
                    for entry_line in entry.line_ids:
                        if entry_line.credit == 0:
                            gen_entry.append((4, entry_line.id))
            mpesa_id = mpesa_obj.create({'salesrep_id': salesrep_id,
                                         'date': date,
                                         'route_id': route_id,
                                         'amount': payment_amount,
                                         'mpesa_ref': mpesa_ref,
                                         'payment_method_id': payment_method_id,
                                         'cash_payment_method_id': cash_payment_method_id,
                                         'customer_payments_ids': gen_entry})
            mpesa_id.action_post()
            result.update(
                {'message': 'Mpesa successfully created with mpesa ref: ' + mpesa_ref, 'mpesa id': mpesa_id.id,
                 'result': True})
        except Exception as e:
            result.update({'message': e, 'result': False})
        return result
