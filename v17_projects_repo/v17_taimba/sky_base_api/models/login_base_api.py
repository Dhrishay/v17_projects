from odoo import fields, models, api, _
from odoo import http
from odoo.http import request


class BseApi(models.Model):

    _name = 'base.api'

    @http.route('/user_authenticate', type='json', auth='user')
    def user_auth(self, db, login, password):
        user_id = request.session.authenticate(
            db,
            login=login,
            password=password,
        )
        user = request.env['res.users'].browse(user_id)
        return user.id, user.token, user.type
