# -*- encoding: utf-8 -*-
#######################################################################################
#
#    Copyright (C) 2019 Skyscend Business Solutions (https://www.skyscendbs.com)
#    Copyright (C) 2020 Skyscend Business Solutions  Pvt. Ltd.(<https://skyscendbs.com>)
#
#######################################################################################
from odoo import api, fields, models, _


class SaleReport(models.Model):
    _inherit = "sale.report"

    route_id = fields.Many2one('stock.warehouse', 'Route')

    def _query(self):
        with_ = self._with_sale()
        base_query = super()._query()
        fields_clause = ", s.route_id as route_id"
        # Ensure with_ is correctly formatted for the WITH clause
        with_clause = f"WITH {with_} " if with_ else ""

        # Construct the query string with additional fields
        query = f"""
            {with_clause}
            SELECT {self._select_sale()}{fields_clause}
            FROM {self._from_sale()}
            WHERE {self._where_sale()}
            GROUP BY {self._group_by_sale()}
            {")" if with_ else ""}
        """

        return query.strip()






