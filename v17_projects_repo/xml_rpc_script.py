from xmlrpc import client as xmlrpclib
import xlrd
import base64
import requests

username = 'tech@micromutiny.com' #the user
password = 'AnupNinja2024!'      #the password of the user
dbname = 'unigroupnz'
server = 'https://unigroupnz.odoo.com/'

# sock_common = xmlrpclib.ServerProxy('https://'+ server +'/xmlrpc/2/common')
sock_common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % server)
uid = sock_common.login(dbname, username, password)
sock = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % server, allow_none=True)
print("\n\nsock:::::::::::>>>>>>>>>>", sock)

wb = xlrd.open_workbook('/tmp/Customer_Product_Download_Ross_Final.xlsx')
sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')
value_list = []
for items in range(2, sheet_name.nrows):
    # image_url = sheet_name.cell_value(items, 15)
    # response = requests.get(image_url)
    # image_content = response.content
    attribute_1 = sheet_name.cell_value(items, 2)
    option_value_1 = sheet_name.cell_value(items, 3)
    print('\n\n::::::::::::;option_value_1', option_value_1)
    attr_value = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search', [[['name', '=', str(option_value_1)]]])
    uom_categ_rec = sock.execute_kw(dbname, uid, password, 'uom.category', 'search', [[['name', '=', 'Unit']]])
    if sheet_name.cell_value(items, 3):
        value_list.append(attr_value and attr_value[0])

    uom_data = sheet_name.cell_value(items, 9).split(' ')
    print('\n\n::::::::::::;uom_data', uom_data)
    uom_rec = sock.execute_kw(dbname, uid, password, 'uom.uom', 'search', [[['name', '=', sheet_name.cell_value(items, 9)]]])
    uom_id = uom_rec
    print('\n\n::::::::::::;uom_data', uom_id)
    if not uom_rec:
        uom_dict = {
            'name': sheet_name.cell_value(items, 9) or '',
            'uom_type': 'bigger',
            'ratio': uom_data and uom_data[0] or 0,
            'active': 't',
            'rounding': 0.01000,
            'category_id': uom_categ_rec and uom_categ_rec[0],
        }
        uom_rec_id = sock.execute_kw(dbname, uid, password, 'uom.uom', 'create', [uom_dict])
        uom_id = [uom_rec_id] 

    print('\n\n::::::::::::;value_list', value_list)
    print('\n\n::::::::::::;uom_data111111111111111111', uom_id)
    if sheet_name.cell_value(items, 4):
        product_template_vals = {
            'default_code': sheet_name.cell_value(items, 0),
            'name': sheet_name.cell_value(items, 5),
            'barcode': sheet_name.cell_value(items, 12),
            'description': sheet_name.cell_value(items, 16),
            'description_sale': sheet_name.cell_value(items, 6),
            # 'image_1920': xmlrpclib.Binary(image_content),
            'sale_line_warn_msg': sheet_name.cell_value(items, 0),
            'uom_id': uom_id and uom_id[0],
            'uom_po_id': uom_id and uom_id[0],
            'detailed_type': 'product'
        }
        sock.execute_kw(dbname, uid, password, 'product.template', 'create', [product_template_vals])
    product_template = sock.execute_kw(dbname, uid, password, 'product.template', 'search', [[['sale_line_warn_msg', '=', sheet_name.cell_value(items, 0)]]])
    att_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_1]]])
    print('\n\n::::::::::::product_template', product_template)
    if product_template:
        default_code = sock.execute_kw(dbname, uid, password, 'product.template', 'read', product_template, {'fields': ['default_code']})
        print('\n\n::::::::::::default_code', default_code, att_id)
        if default_code and default_code[0].get('default_code') == sheet_name.cell_value(items, 0):
            if sheet_name.cell_value(items, 4) and att_id and value_list != []:
                sock.execute_kw(dbname, uid, password, 'product.template', 'write', [product_template, {'attribute_line_ids': [(0, 0, {'attribute_id': att_id[0], 'value_ids': [(6, 0, value_list)]})]}])
                value_list.clear()

for items in range(2, sheet_name.nrows):
    if not sheet_name.cell_value(items, 6):
        product_template = sock.execute_kw(dbname, uid, password, 'product.template', 'search', [[['sale_line_warn_msg', '=', sheet_name.cell_value(items, 0)]]])
        prod_recs = sock.execute_kw(dbname, uid, password, 'product.product', 'search', [[['product_tmpl_id', '=', product_template[0]]]])
        for prod in prod_recs:
            prod_tmp_var_att = sock.execute_kw(dbname, uid, password, 'product.product', 'read', [prod], {'fields': ['product_template_variant_value_ids']})
            if not prod_tmp_var_att[0].get('product_template_variant_value_ids') and sheet_name.cell_value(items, 3) and sheet_name.cell_value(items, 5):
                 sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {'default_code': sheet_name.cell_value(items, 1), 'barcode': sheet_name.cell_value(items, 12)}])
                 break
            prod_att_val = sock.execute_kw(dbname, uid, password, 'product.template.attribute.value', 'read', [prod_tmp_var_att[0].get('product_template_variant_value_ids')], {'fields': ['product_attribute_value_id']})
            for i in prod_att_val[0].get('product_attribute_value_id')[0]:
                att_val = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'read', [i], {'fields': ['name']})
                if att_val and att_val[0].get('name') == sheet_name.cell_value(items, 3):
                    sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {'default_code': sheet_name.cell_value(items, 1), 'barcode': sheet_name.cell_value(items, 14)}])
                    break
                if att_val and att_val[0].get('name') == sheet_name.cell_value(items, 5):
                    sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {'default_code': sheet_name.cell_value(items, 1), 'barcode': sheet_name.cell_value(items, 14)}])
                    break


# product_package_lst = []
# for items in range(2, sheet_name.nrows):
#     prod_recs = sock.execute_kw(dbname, uid, password, 'product.product', 'search', [[['default_code', '=', sheet_name.cell_value(items, 1)]]])
#     if prod_recs:
#         if sheet_name.cell_value(items, 10):
#             pkg_type = sock.execute_kw(dbname, uid, password, 'stock.package.type', 'search', [[['name', '=', 'Pack']]])
#             qty = sheet_name.cell_value(items, 10) and sheet_name.cell_value(items, 10).split(' ') or 0.0
#             product_packaging = {
#                 'name': sheet_name.cell_value(items, 10),
#                 'product_id': prod_recs and prod_recs[0],
#                 'sales': True,
#                 'package_type_id': pkg_type and pkg_type[0],
#                 'qty':  float(qty[0]),
#                 'barcode': sheet_name.cell_value(items, 13) if sheet_name.cell_value(items, 13) else None,
#             }
#             product_package_lst.append(product_packaging)
#         if sheet_name.cell_value(items, 11):
#             pkg_type = sock.execute_kw(dbname, uid, password, 'stock.package.type', 'search', [[['name', '=', 'Carton']]])
#             qty = sheet_name.cell_value(items, 11) and sheet_name.cell_value(items, 11).split(' ') or 0.0
#             product_packaging = {
#                 'name': sheet_name.cell_value(items, 11),
#                 'product_id': prod_recs and prod_recs[0],
#                 'sales': True,
#                 'package_type_id': pkg_type and pkg_type[0],
#                 'qty': float(qty[0]),
#                 'barcode': sheet_name.cell_value(items, 14) if sheet_name.cell_value(items, 14) else None,
#             }
#             product_package_lst.append(product_packaging) 
# if product_package_lst:
#     for pack in product_package_lst:
#         print('\n\n:::::::::::PACK', pack)
#         sock.execute_kw(dbname, uid, password, 'product.packaging', 'create', [pack])
#sock.execute_kw(dbname, uid, password, 'res.company', 'import_products', [1])
print('\n\n:::::::Script Execute Successfully')
