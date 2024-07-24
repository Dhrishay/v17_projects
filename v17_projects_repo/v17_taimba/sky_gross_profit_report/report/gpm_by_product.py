from odoo import api, fields, models, tools, _


class GPMProductReport(models.Model):
    _name = 'gpm.product.report'
    _description = "Gross Profit Analysis Report"
    _auto = False

    
    date = fields.Date()
    product_id = fields.Many2one('product.product')
    partner_id = fields.Many2one('res.partner')
    order_id = fields.Many2one('sale.order')
    cost = fields.Float()
    sale_price = fields.Float()
    margin_per = fields.Float('Margin%')
    margin = fields.Float('Margin')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)

        self._cr.execute("""
        CREATE or REPLACE view %s as (
                SELECT
                    sol.id as id,
                    so.id as order_id,
                    so.date_order as date,
                    so.partner_id as partner_id,
                    sol.price_unit as sale_price,
                    sol.margin as margin,
                    sol.purchase_price as cost,
                    sol.product_id as product_id,
                    sol.margin_percent as margin_per
                    from sale_order as so, 
                    sale_order_line sol where
                    sol.order_id = so.id);
        """ % self._table)