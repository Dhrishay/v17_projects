# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import _, api, exceptions, fields, models


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = [
        'account.move.line',
        'ecofi.validation.mixin',
    ]

    # region Fields

    ecofi_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Move Tax',
    )
    ecofi_account_counterpart = fields.Many2one(
        string='Account Counterpart',
        comodel_name='account.account',
        ondelete='restrict',
    )
    line_ref = fields.Char()

    # endregion

    # region Constrains

    @api.constrains('tax_ids')
    def _check_tax_ids(self):
        print("\n\n\n_check_tax_ids-----------------------------------")
        for line in self.filtered(lambda l: l.company_id.uses_skr()):
            if len(line.tax_ids) > 1:
                raise exceptions.ValidationError(_(
                    'Error! There can only be one tax per invoice line.'
                ))

    # endregion

    # region CRUD
    #done
    @api.model_create_multi
    def create(self, vals_list):
        print("\n\n\ncreate----------------------------------")
        print("vals_list---------------------",vals_list)
        for vals in vals_list:
            tax_ids = vals.get('tax_ids') or []  # tax_ids can be False
            print("tax_ids-----------111111-----------------",tax_ids)
            # print("tax_ids---------22222-------------------",tax_ids[0])
            # print("tax_ids---------333333-------------------",tax_ids[0][1])
            if not vals.get('ecofi_tax_id') and tax_ids and tax_ids[0][1]:
                print("tax_ids[0][1]------------------",tax_ids[0][1])
                # account.payment transfers the actual ids in a set
                vals['ecofi_tax_id'] = tax_ids[0][1]
                print("vals['ecofi_tax_id']------------------",vals['ecofi_tax_id'])
        return super().create(vals_list)

    # endregion

    # region Business Methods

    def _ecofi_validations_enabled(self):
        print("\n\n\n_ecofi_validations_enabled--------move line---------------")
        print("self.move_id._ecofi_validations_enabled()----------------",self.move_id._ecofi_validations_enabled())
        return self.move_id._ecofi_validations_enabled()

    def name_get(self):
        print("\n\n\nname_get------------>>>>>>>>>>-------------------")
        if self.env.context.get('counterpart_name'):
            result = []
            for line in self:
                if line.ref:
                    result.append(
                        (line.id, (line.name or '') + ' (' + line.ref + ')'),
                    )
                else:
                    result.append((line.id, line.name))
            print("result------------------",result)
            aaaaaaaaaaazzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
            return result
        return super().name_get()

    @api.ecofi_validate('validate_tax_count')
    def _validate_tax_count(self):
        print("\n\n\n_validate_tax_count--------------------------------")
        """
        Check if there is at most one tax in the line.
        """

        self.ensure_one()

        is_valid = len(self.tax_ids) <= 1
        print("is_valid----------------------",is_valid)
        if not is_valid:
            raise exceptions.ValidationError(_('More than one tax specified!'))

    # endregion
