# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from ..exceptions import FinanceinterfaceException


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = [
        'account.move',
        'ecofi.validation.mixin',
    ]

    # region Fields

    vorlauf_id = fields.Many2one(
        comodel_name='ecofi',
        string='Export',
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    ecofi_buchungstext = fields.Char(
        string='Export Voucher Text',
        size=60,
    )
    ecofi_manual = fields.Boolean(
        string='Set Counter accounts manually',
    )
    ecofi_to_check = fields.Boolean(
        string='Verify',
    )
    ecofi_validations_enabled = fields.Boolean(
        string='Perform Validations',
        default=True,
    )
    delivery_date = fields.Date(
        help='Enter the delivery period (e.g. month) or the delivery date here.'
    )
    delivery_date_exists = fields.Boolean(
        compute='_compute_delivery_date_exists',
    )
    line_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='move_id',
        string='Journal Items',
        copy=True,
        readonly=False,
    )
    # endregion

    # region CRUD
    #done
    def unlink(self):
        """
        Prevent exported moves from being deleted.
        """
        for thismove in self:
            if self.env.context.get('delete_none', False):
                continue
            if thismove.vorlauf_id:
                raise FinanceinterfaceException(
                    _(
                        'Warning! Account moves which are already in an '
                        'export can not be deleted!'
                    )
                )
        return super().unlink()

    # endregion

    # region View
    #done
    def button_cancel(self):
        """
        Check if the move has already been exported.
        """
        res = super().button_cancel()
        for move in self:
            if move.vorlauf_id:
                raise FinanceinterfaceException(
                    _('Error! You cannot modify an already exported move.')
                )
        return res

    # endregion

    # region Business Methods

    def _post(self, soft=True):
        print("\n\n\n_post----------------ecoserive0--------------")
        """
        Perform checks if a move is posted.
        """
        error_msg = self.perform_validations()
        print("error_msg------------------",error_msg)
        if error_msg:
            print("if error_msg----------------------------")
            raise ValidationError('\n\n'.join(error_msg))
        return super()._post(soft=soft)

    def _ecofi_validations_enabled(self) -> bool:
        print("\n\n\n_ecofi_validations_enabled-------------------------------")
        return self.ecofi_validations_enabled

    def perform_validations(self):
        print("\n\n\nperform_validations-----------------------------")
        result = super().perform_validations()
        print("result-------------------------",result)
        for number, line in enumerate(self.line_ids, start=1):
            print("for--------------------")
            print("number--------------------",number)
            print("line--------------------",line)
            result.extend([
                _('Line {number}: {validation}').format(
                    number=number,
                    validation=validation,
                )
                for validation in line.perform_validations()
            ])
            print("result--------------------",result)
        return result

    # endregion

    def _compute_delivery_date_exists(self):
        print("\n\n\n_compute_delivery_date_exists------------------------------")
        is_installed = False
        modules = self.sudo().env['ir.module.module'].search([
            ('name', '=', 'ecoservice_german_documents_invoice'),
        ])
        print("modules------------------------",modules)
        if modules and modules.state in ['installed']:
            print("if compute---------------------")
            is_installed = True
        for record in self:
            record.delivery_date_exists = is_installed
