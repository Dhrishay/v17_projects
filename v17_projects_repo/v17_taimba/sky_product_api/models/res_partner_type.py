# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import api, models,fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type_id = fields.Many2one('customer.type', string='Customer Type')

    @api.onchange('customer_type_id', 'route_id')
    def _onchange_type(self):
        pricelist = self.env["product.pricelist"].search([('customer_type_id','=',self.customer_type_id.id),
                                                          ('route_id','=',self.route_id.id),
                                                          ('name','=','Public Pricelist')])
        if pricelist:
            self.property_product_pricelist = pricelist
        else:
            self.property_product_pricelist = self.env.ref('sky_product_api.list0')
        result = {
            'domain': {
                'property_product_pricelist': pricelist.ids
            }
        }
        return result
