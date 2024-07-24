from odoo import api, fields, models, SUPERUSER_ID, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_date', 'company_id')
    def _compute_date(self):
        res = super(AccountMove, self)._compute_date()
        for move in self:
            if move.invoice_date:
                if fields.datetime.now().month != move.invoice_date.month:
                    move.name = False
        return res

    def write(self, vals):
        # OVERRIDE
        for move in self:
            if vals.get('date'):
                move.name = False
            if vals.get('invoice_date'):
                move.name = False
        res = super(AccountMove, self).write(vals)
        return res
    
    def update_seq(self):
        for rec in self:
            replace_month = rec.name.replace(rec.name[10:12], str(rec.date.month))
            new_name = replace_month.replace(replace_month[:4], rec.journal_id.code)
            rec.name = new_name


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def write(self, vals):
        # OVERRIDE
        if vals.get('date'):
            self.name = False
        res = super().write(vals)
        return res
