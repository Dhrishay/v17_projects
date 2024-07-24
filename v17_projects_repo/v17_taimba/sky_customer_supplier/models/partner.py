from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'
    
    customer_rank_boolean = fields.Boolean()
    supplier_rank_boolean = fields.Boolean()

    def compute_domain(self, type):
        """
         Append Is customer true domain if customer invoice/refund/receipt else append Is vendor true domain
        :param type: Type of Invoice/refund/receipt
        :return: Domain
        """
        if type in ['out_invoice', 'out_refund', 'out_receipt', 'inbound']:
            domain = [('customer_rank', '>', 0)]
        else:
            domain = [('supplier_rank', '>', 0)]
        return domain

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        """
            Override _name_search in order to add domain of Is customer and Is vendor fields.
        """
        if self._context.get('move_type'):
            domain += self.compute_domain(self._context.get('move_type'))
        elif self._context.get('payment_type'):
            domain += self.compute_domain(self._context.get('payment_type'))
        return super(Partner, self)._name_search(name, domain=domain, operator=operator, limit=limit,
                                                 order=order)

    @api.onchange('customer_rank')
    def change_customer_rank(self):
        for rec in self:
            if rec.customer_rank > 0:
                rec.customer_rank_boolean = True

    @api.onchange('supplier_rank')
    def change_supplier_rank(self):
        for rec in self:
            if rec.supplier_rank > 0:
                rec.supplier_rank_boolean = True

    @api.onchange('customer_rank_boolean')
    def change_customer_rank_flag(self):
        for rec in self:
            if rec.customer_rank_boolean:
                rec._increase_rank('customer_rank')
            if rec.customer_rank_boolean == False:
                rec.customer_rank = 0
                
    @api.onchange('supplier_rank_boolean')
    def change_supplier_rank_flag(self):
        for rec in self:
            if rec.supplier_rank_boolean:
                rec._increase_rank('supplier_rank')
            if rec.supplier_rank_boolean == False:
                rec.supplier_rank = 0
            
    def update_customers(self):
        for rec in self:
            if rec.customer_rank > 0:
                rec.customer_rank_boolean = True
            if rec.supplier_rank > 0:
                rec.supplier_rank_boolean = True
            