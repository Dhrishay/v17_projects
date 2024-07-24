from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, ValidationError


class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target'

    def _get_start_date(self):
        start_date = datetime.today().replace(day=1)
        return start_date.date()

    def last_day_of_month(self, date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month + 1, day=1) - timedelta(days=1)

    def _get_end_date(self):
        end_date = self.last_day_of_month(datetime.today())
        return end_date.date()

    name = fields.Char()
    user_id = fields.Many2one('res.users', string="Salesperson")
    start_date = fields.Date('Start Date', default=lambda self: self._get_start_date())
    end_date = fields.Date('End Date', default=lambda self: self._get_end_date())
    route_id = fields.Many2one('stock.warehouse', string="Route")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    total_target = fields.Monetary('Total Target', compute='_compute_target', store=True)
    work_day = fields.Integer('Working Days')
    daily_target = fields.Monetary('Daily Target', compute='_compute_daily_target', store=True)
    lines_ids = fields.One2many('sales.target.line', 'target_id')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('cancel', 'Cancelled')],
                             string="Status", readonly=True, default='draft')

    @api.constrains('user_id', 'start_date', 'start_date')
    def check_date(self):
        for record in self:
            sales_id = self.env['sales.target'].search(
                [('id', '!=', record.id), ('user_id', '=', self.user_id.id), ('start_date', '=', self.start_date),
                 ('end_date', '=', self.end_date), ('route_id', '=', self.route_id.id)], limit=1)
            if sales_id:
                raise ValidationError(
                    'Sales Target for same user with this route has already been created for same time period!')

    @api.depends('lines_ids')
    def _compute_target(self):
        for line in self:
            total = 0
            for line in line.lines_ids:
                total = line.sub_total + total
                self.total_target = total

    @api.depends('total_target', 'lines_ids', 'work_day')
    def _compute_daily_target(self):
        if self.work_day != 0.0:
            daily_target = (int(self.total_target) / self.work_day)
            self.daily_target = daily_target

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sales.target') or ('New')
        result = super(SalesTarget, self).create(vals)
        return result

    def unlink(self):
        for load in self:
            if load.state == 'confirm':
                raise UserError(_("You can't delete data in Confirmed state"))
            elif load.state == 'cancel':
                raise UserError(_("You can't delete data in Cancelled state"))
        rec = super(SalesTarget, self).unlink()
        return rec


class SalesTargetLine(models.Model):
    _name = 'sales.target.line'
    _description = 'Sales Target Line'

    target_id = fields.Many2one('sales.target')
    product_id = fields.Many2one('product.product')
    sales_qty = fields.Float('Quantity')
    uom = fields.Many2one('uom.uom')
    price = fields.Float('Price')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    sub_total = fields.Monetary(string='Sub Total', compute='_compute_amount')

    @api.depends('sales_qty', 'price')
    def _compute_amount(self):
        for line in self:
            total = line.price * line.sales_qty
            line.sub_total = total

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.uom = self.product_id.uom_id
            self.price = self.product_id.lst_price
        