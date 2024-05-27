from odoo import models, fields


class StockClean(models.Model):
    _name = 'stock.location.clean'
    _rec_name = 'stock_location_id'

    stock_location_id = fields.Many2one('stock.location', string='Location', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now(), required=True)
    status = fields.Selection([('draft', 'Draft'),
                               ('in_progress', 'In Progress'),
                               ('done', 'Done')], default='draft', string='Status')
    stock_line_ids = fields.One2many('stock.clean.line', 'stock_clean_id', string='Stock Lines')

    def action_confirm(self):
        for location in self:
            location.status = 'in_progress'

    def action_done(self):
        for location in self:
            location.status = 'done'

        previous_clean_record = self.search([('date', '<=', self.date),
                                             ('id', '!=', self.id)], order='date desc', limit=1)

        st_move_line_domain = [('location_dest_id', '=', self.stock_location_id.id),
                               ('state', '=', 'done')]
        if previous_clean_record:
            st_move_line_domain += [('date', '>', previous_clean_record.date), ('date', '<=', self.date)]
        else:
            st_move_line_domain.append(('date', '<=', self.date))
        st_move_lines = self.env['stock.move.line'].search(st_move_line_domain)
        product_cln_lst = []
        for mv_line in st_move_lines:
            vals = {
                'product_id': mv_line.product_id.id,
                'lot_serial_id': mv_line.lot_id.id,
                'time_of_production': mv_line.move_id.production_id.date_finished,
                'total_weight': mv_line.quantity * mv_line.product_id.weight,
                'sale_order_id': mv_line.move_id.sale_line_id.order_id.id,
                'purchase_order_id': mv_line.move_id.purchase_line_id.order_id.id,
            }
            if vals.get('sale_order_id'):
                vals.update({'partner_id': mv_line.move_id.sale_line_id.order_id.partner_id.name})
            if vals.get('purchase_order_id'):
                vals.update({'partner_id': mv_line.move_id.purchase_line_id.order_id.partner_id.name})

            product_cln_lst.append((0, 0, vals))
        if product_cln_lst:
            self.stock_line_ids = product_cln_lst

    def action_set_to_draft(self):
        self.stock_line_ids = [5, 0, 0]
        for location in self:
            location.status = 'draft'






