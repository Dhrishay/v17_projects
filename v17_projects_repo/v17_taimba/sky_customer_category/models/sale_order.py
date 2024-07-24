from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    all_pricelist_ids = fields.Many2many('product.pricelist', string='All Pricelist')


    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        super()._compute_pricelist_id()
        pricelist = self.env['product.pricelist'].search([])
        for order in self:
            if order.partner_id.partner_categ_id:
                pricelist_id = self.env['product.pricelist'].search(
                    [('category_id', '=', order.partner_id.partner_categ_id.id)])
                if pricelist_id:
                    order.pricelist_id = pricelist_id[0].id
                    order.all_pricelist_ids = pricelist_id.ids
            else:
                order.all_pricelist_ids = pricelist.ids