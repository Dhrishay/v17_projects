import json
import logging
import functools

import werkzeug.wrappers

from odoo import http
from odoo.addons.sky_base_api.common import invalid_response, valid_response
from odoo.http import request
from odoo.exceptions import AccessError, AccessDenied

_logger = logging.getLogger(__name__)

expires_in = "sky_base_api.access_token_expires_in"


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

        # Update the environment with the user's ID
        request.env = request.env(user=request.session.uid)
        return func(self, *args, **kwargs)
    return wrap


class AuthTokenUser(http.Controller):
    # @validate_token
    @http.route("/user_login", type="json", auth="none", csrf=False, cors='*')
    def user_auth(self, db, password, login):
        user_phone = request.env['res.users'].sudo().search([('phone_number', '=', login)])
        user_login = user_phone.login
        try:
            user_id = request.session.authenticate(
                db,
                login=user_login or login,
                password=password,
            )
        except Exception as e:
            return {
                'result': False, 'message': 'UserName or Password is Invalid!'
            }
        else:
            user = request.env['res.users'].sudo().browse(user_id)
            _token = request.env["api.access_token"]
            access_token = _token.find_one_or_create_token(user_id=user_id, create=True)
            user_dict = ({'user_id': user.id,
                                    'user_token': access_token,
                                    'user_type': user.user_type,
                                    'phone_number': user.phone_number,
                                    'user_name': user_login or login,
                                    'user_route': user.route_ids and user.route_ids[0].id,  # for ecommerce
                                    'route_name': user.route_ids and user.route_ids[0].name,  # for ecommerce
                                    })
        return user_dict


class AccessToken(http.Controller):
    """."""

    def __init__(self):

        self._token = request.env["api.access_token"]
        self._expires_in = request.env.ref(expires_in).sudo().value

    def auth_token(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           eq = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))
        """
        _token = request.env["api.access_token"]
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credentials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing error", "either of the following are missing [db, username,password]", 403,
                )
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = _token.find_one_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    "user_context": request.session.get_context() if uid else {},
                    "company_id": request.env.user.company_id.id if uid else None,
                    "company_ids": request.env.user.company_ids.ids if uid else None,
                    "partner_id": request.env.user.partner_id.id,
                    "token": access_token,
                    "expires_in": self._expires_in,
                }
            ),
        )

    @http.route("/user_logout", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete(self, **post):
        """."""
        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("token")
        access_token = _token.search([("token", "=", access_token)])
        if not access_token:
            info = "No access token was provided in request!"
            error = "Access token is missing in the request header"
            _logger.error(info)
            return invalid_response(400, error, info)
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response([{"desc": "access token successfully deleted", "delete": True}])

    @validate_token
    @http.route('/CustomerRegistration', type='json', auth='user')
    def customer_registration(self, lastname, firstname, phone, email, route):
        result = {}
        try:
            user = request.env['res.users'].create({
                'lastname': lastname,
                'firstname': firstname,
                'login': email,
                'phone': phone,  # Assuming the field name is 'phone', not 'phone_number'
                'route_ids': [(6, 0, [route])],  # Wrap route in a list as expected by 'create' method
                'user_type': 'customer',
                'sel_groups_1_9_10': 9
            })
            result.update({
                'message': 'Customer successfully registered',
                'id': user.id,
                'type': user.user_type,
                'result': True
            })
        except Exception as e:
            result.update({'message': str(e), 'result': False})  # Convert exception to string for better error handling
        return result
