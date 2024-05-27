from odoo import models, fields, api
import xlrd
from odoo.modules.module import get_module_path
import base64
import requests


class ResCompany(models.Model):
    _inherit = 'res.company'

    def import_products(self):
        self.import_product_template()
        self.update_reference()
        self.product_packaging()
        return True

    def import_product_template(self):
        module_path = get_module_path('product_import')
        file_path = module_path + '/script/Customer_Product_Download_Ross_Final.xlsx'
        wb = xlrd.open_workbook(file_path)
        sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')

        product_attribute = {}
        product_variant_lst = []
        attr_value_dict = {}
        att_dict = {}
        value_list = []

        for prd_attr in self.env['product.attribute'].search([]):
            product_attribute.update({prd_attr.name: prd_attr.id})

        for prd_attr_value in self.env['product.attribute.value'].search([]):
            attr_value_dict.update({prd_attr_value.name: prd_attr_value.id})

        for items in range(2, sheet_name.nrows):
            image_url = sheet_name.cell_value(items, 15)
            response = requests.get(image_url)
            image_content = response.content
            attribute_1 = sheet_name.cell_value(items, 2)
            option_value_1 = sheet_name.cell_value(items, 3)

            # attribute create>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            if attribute_1 in product_attribute:
                prd_attr_id = product_attribute.get(attribute_1)
            else:
                prd_attr_id = self.env['product.attribute'].create({'name': attribute_1}).id
                product_attribute.update({attribute_1: prd_attr_id})

            # value create>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            att_id = self.env['product.attribute'].search([('name', '=', attribute_1)])

            if option_value_1:
                if option_value_1 in attr_value_dict:
                    value_id = attr_value_dict.get(option_value_1)
                else:
                    value_id = self.env['product.attribute.value'].create(
                        {'name': option_value_1, 'attribute_id': att_id.id}).id
                    attr_value_dict.update({option_value_1: value_id})

            # product template create >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            attr_value = self.env['product.attribute.value'].search([('name', '=', str(option_value_1))])

            if sheet_name.cell_value(items, 3):
                value_list.append(attr_value.id)

            if sheet_name.cell_value(items, 4):
                product_template_vals = {
                    'default_code': sheet_name.cell_value(items, 0),
                    'name': sheet_name.cell_value(items, 5),
                    'barcode': sheet_name.cell_value(items, 12),
                    'description': sheet_name.cell_value(items, 16),
                    'description_sale': sheet_name.cell_value(items, 6),
                    'image_1920': base64.b64encode(image_content),
                    'sale_line_warn_msg': sheet_name.cell_value(items, 0)
                }
                prd_temp = self.env['product.template'].create(product_template_vals)

# # # # >>>>>>>>>>>>>>>>>>>> product template complete >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..

# # ###################### product variant create>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            product_template = self.env['product.template'].search([('sale_line_warn_msg', '=', sheet_name.cell_value(items, 0))])

            att_id = self.env['product.attribute'].search([('name', '=', attribute_1)])
            # attr_value = self.env['product.attribute.value'].search([('name', '=', str(option_value_1))])

            if product_template.default_code == sheet_name.cell_value(items, 0):
                # if sheet_name.cell_value(items, 3):
                #     value_list.append(attr_value.id)
                if sheet_name.cell_value(items, 4) and value_list != []:
                    product_template.write({
                        'attribute_line_ids': [
                            (0, 0, {
                                'attribute_id': att_id.id,
                                'value_ids': [(6, 0, value_list)]
                            })
                        ],

                    })
                    value_list.clear()

    def update_reference(self):
        module_path = get_module_path('product_import')
        file_path = module_path + '/script/Customer_Product_Download_Ross_Final.xlsx'
        wb = xlrd.open_workbook(file_path)
        sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')
        for items in range(2, sheet_name.nrows):
            product_product = self.env['product.product'].search([('name', '=', sheet_name.cell_value(items, 5))])
            prd_filter = product_product.filtered(lambda l: l.product_tmpl_id.sale_line_warn_msg == sheet_name.cell_value(items,0)
                                                  and l.product_template_variant_value_ids.name == sheet_name.cell_value(items, 3))
            if prd_filter:
                prd_filter.write({'default_code': sheet_name.cell_value(items, 1),
                                 'barcode': sheet_name.cell_value(items, 12)})
        self._cr.execute("UPDATE product_template SET sale_line_warn_msg = NULL")

    def product_packaging(self):
        module_path = get_module_path('product_import')
        file_path = module_path + '/script/Customer Product Download_packaging.xlsx'
        wb = xlrd.open_workbook(file_path)
        sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')
        product_package_lst = []
        for items in range(3, sheet_name.nrows):
            product_variant = self.env['product.product'].search([('default_code', '=', sheet_name.cell_value(items, 1))])
            if product_variant:
                if sheet_name.cell_value(items, 9):
                    package_type_id = self.env['stock.package.type'].search([('name', '=', 'Pack')]).id
                    product_packaging = {
                        'name': sheet_name.cell_value(items, 9),
                        'product_id': product_variant.id,
                        'sales': True,
                        'package_type_id': package_type_id,
                        'qty':  sheet_name.cell_value(items, 8),
                        'barcode': sheet_name.cell_value(items, 13) if sheet_name.cell_value(items, 13) else None,
                    }
                    product_package_lst.append(product_packaging)

                if sheet_name.cell_value(items, 10):
                    package_type_id = self.env['stock.package.type'].search([('name', '=', 'Carton')]).id
                    product_packaging = {
                        'name': sheet_name.cell_value(items, 10),
                        'product_id': product_variant.id,
                        'sales': True,
                        'package_type_id': package_type_id,
                        'qty': sheet_name.cell_value(items, 11),
                        'barcode': sheet_name.cell_value(items, 14) if sheet_name.cell_value(items, 14) else None,
                    }
                    product_package_lst.append(product_packaging)

        self.env['product.packaging'].create(product_package_lst)
