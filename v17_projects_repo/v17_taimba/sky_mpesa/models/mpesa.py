# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError


class MpesaPayment(models.Model):
    _name = 'mpesa.payment'
    _description = 'Mpesa Payment'
    _rec_name = 'mpesa_ref'

    name = fields.Char("Name", copy=False, index=True)
    salesrep_id = fields.Many2one("res.users", string='Sales Rep')
    salesrep_partner_id = fields.Many2one('res.partner', related='salesrep_id.partner_id', string='SalesRep Partner')
    route_id = fields.Many2one("stock.warehouse", string="Route")
    date = fields.Date(string="Date")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    amount = fields.Monetary(currency_field='currency_id', string="Payment Amount", help="Enter payment amount.")
    phone_number = fields.Char("Phone Number")
    mpesa_ref = fields.Char(string="Mpesa Ref.")
    payment_method_id = fields.Many2one("account.journal", string="Payment Method")
    cash_payment_method_id = fields.Many2one("account.journal", string=" Cash Payment Method")
    cash_account_id = fields.Many2one('account.account', related='cash_payment_method_id.default_account_id',
                                      string='Cash Account')
    state = fields.Selection([('draft', 'Draft'),
                              ('posted', 'Posted'),
                              ('cancelled', 'Cancelled'),
                              ], 'State', default='draft')
    customer_payments_ids = fields.Many2many("account.move.line", string='Customer Payments')
    total_amount = fields.Float(string='Total Amount', compute='_total_calc')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    payment_count = fields.Integer(string='Payment Count', compute='_get_payment_count', readonly=1, copy=False)

    def unlink(self):
        for load in self:
            if load.state == 'cancelled':
                raise UserError(_("You can't delete data in Cancelled state"))
        rec = super(MpesaPayment, self).unlink()
        return rec

    def _get_payment_count(self):
        """
        This method will count the numbers of payments created.
        -------------------------------------------------------------------
        @param self: object pointer
        """
        payment_obj = self.env['account.move']
        for payment in self:
            payment.payment_count = payment_obj.search_count([('mpesa_id', '=', payment.id)])

    def action_view_payment(self):
        """
        This method will return the payment of same mpesa.
        --------------------------------------------------
        @param self: object pointer
        """
        action = self.env.ref('sky_mpesa.action_move_journal_line_inherit').read()[0]
        action['domain'] = [('mpesa_id.id', '=', self.id)]
        return action

    @api.depends('customer_payments_ids')
    def _total_calc(self):
        if self.customer_payments_ids:
            for lines in self.customer_payments_ids:
                self.total_amount += lines.debit + lines.credit
        else:
            self.total_amount = 0.00

    def action_post(self):
        seq = self.env['ir.sequence'].next_by_code('mpesa.sequences')
        self.name = seq
        self.state = 'posted'
        account_move_obj = self.env['account.move']
        # recon_obj = self.env['account.reconciliation.widget']
        move_vals = {'move_type': 'entry',
                     'ref': self.name,
                     'date': self.date,
                     'pay_ref': self.mpesa_ref,
                     'mpesa_id': self.id}
        pay_move_vals = move_vals.copy()
        move_vals.update({'journal_id': self.payment_method_id.id,
                          'line_ids': [(0, 0, {"account_id": self.company_id.transfer_account_id.id,
                                               "partner_id": self.salesrep_partner_id.id,
                                               'name': self.name,
                                               "credit": self.amount}),
                                       (0, 0, {"account_id": self.payment_method_id.default_account_id.id,
                                               "partner_id": self.salesrep_partner_id.id,
                                               'name': self.name,
                                               "debit": self.amount})]})
        pay_move_vals.update({'journal_id': self.cash_payment_method_id.id,
                              'line_ids': [(0, 0, {"account_id": self.cash_payment_method_id.default_account_id.id,
                                                   "partner_id": self.salesrep_partner_id.id,
                                                   'name': self.name,
                                                   "credit": self.amount}),
                                           (0, 0, {"account_id": self.company_id.transfer_account_id.id,
                                                   "partner_id": self.salesrep_partner_id.id,
                                                   'name': self.name,
                                                   "debit": self.amount})]})
        payment_move = account_move_obj.sudo().create(move_vals)
        payment_move.action_post()
        cash_payment_move = account_move_obj.sudo().create(pay_move_vals)
        cash_payment_move.action_post()
        cash_move_line_ids = self.customer_payments_ids.ids
        cash_pay_move_line = cash_payment_move.line_ids.filtered(lambda r: r.account_id == self.cash_payment_method_id.default_account_id)
        cash_move_line_ids += cash_pay_move_line.ids
        # recon_obj.sudo()._process_move_lines(cash_move_line_ids, [])

    def cancel(self):
        self.state = 'cancelled'
        for lines in self.customer_payments_ids:
            lines.remove_move_reconcile()
        account_move = self.env['account.move'].search([('mpesa_id', '=', self.id)])
        account_move.button_cancel()
        account_move.write({'mpesa_id': False})

    def reset_to_draft(self):
        self.state = 'draft'
        for lines in self.customer_payments_ids:
            lines.remove_move_reconcile()
        account_move = self.env['account.move'].search([('mpesa_id', '=', self.id)])
        for record in account_move:
            record.mpesa_id = False

