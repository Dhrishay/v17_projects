# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from inspect import getmembers
from typing import Callable, List

from odoo import exceptions, models

ErrorMessages = List[str]
ValidationMethods = List[Callable[..., None]]


class EcofiValidationMixin(models.AbstractModel):
    """
    Perform some kind of validations in the context of the finance interface.

    Example of an implementation::

        class AccountMove(Model):
            _name = 'account.move'
            _inherit = [
                'account.move',
                'ecofi.validation.mixin',
            ]

            @api.ecofi_validate('validate_tax_count')
            def _validate_tax_count(self):
                raise ValidationError('...')
    """

    _name = 'ecofi.validation.mixin'
    _description = 'Helper for easy finance interface validation'

    @property
    def enabled_validations(self) -> ValidationMethods:
        print("\n\n\nenabled_validations---------mixin--------------")
        if not self.company_id.uses_skr():
            print("if not--------------------------------")
            return []

        def is_validation(func):
            # print("\nis_validation----------------------------------")
            return callable(func) and hasattr(func, '_ecofi_validate')

        validation_methods = getmembers(type(self), is_validation)
        print("validation_methods----------------------",validation_methods)

        return [
            method
            for _, method in validation_methods
            if getattr(
                self.company_id.ecofi_validation_id,
                method._ecofi_validate,
            )
        ]

    def _ecofi_validations_enabled(self):
        print("\n\n\n_ecofi_validations_enabled---------mixin-------------")
        raise NotImplementedError

    def perform_validations(self) -> ErrorMessages:
        print("\n\n\nperform_validations-----------mixin----------------------")
        errors = []

        validations = self.enabled_validations

        for rec in self.filtered(
            lambda r: r._ecofi_validations_enabled()
        ):
            for validate in validations:
                try:
                    validate(rec)
                except exceptions.ValidationError as e:
                    errors.append(e.name)

        return errors
