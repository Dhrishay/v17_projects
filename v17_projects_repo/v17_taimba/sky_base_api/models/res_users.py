import random
import string
from odoo.exceptions import AccessDenied

from odoo import _, api, exceptions, fields, models
from odoo import api, models, registry, SUPERUSER_ID
from odoo.http import Response, request


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_default_token(self):
        return ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for i in range(1, 33))

    token = fields.Char(
        string='Token',
        help='Alphanumeric key to login into Odoo',
        default=_get_default_token,
    )

    @api.model_create_multi
    def _set_default_token(self):
        self.token = self._get_default_token()

    @api.constrains('token')
    def _check_token_unique(self):
        ids = self.search([
            ('id', '!=', self.id),
            ('token', '=', self.token),
        ])
        if ids:
            raise exceptions.Warning(_('User token must be unique'))
