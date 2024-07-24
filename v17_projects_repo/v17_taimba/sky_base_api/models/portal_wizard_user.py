from odoo import api, models

class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    @api.model_create_multi
    def _create_user(self):
        user = super()._create_user()
        user._set_default_token()
        return user
