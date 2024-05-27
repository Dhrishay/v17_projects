from xmlrpc import client as xmlrpclib
import xlrd
import base64
import requests
from datetime import datetime

username = 'admin' #the user
password = 'admin'      #the password of the user
dbname = 'v17_product_import_test_new_2903'
server = 'http://0.0.0.0:8082/'

sock_common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % server)
uid = sock_common.login(dbname, username, password)
sock = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % server, allow_none=True)
print("\n\nsock:::::::::::>>>>>>>>>>", sock)

wb = xlrd.open_workbook('/tmp/Customer_Product_Download_Ross_Final.xlsx')
sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')

print('\n\n!!!!!!!!! START Script Execution', datetime.now())
# create a code for existing attribute and value already in database
# ---------------------------------------------------------------------------------------------------
product_attribute = {}
product_attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]])
for att_id in product_attribute_data:
    attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [att_id])
    attribute_name = attribute_data[0]['name']
    existing_value_ids = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search_read', [[('attribute_id', '=', att_id)]], {'fields': ['name', 'id']})
    attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
    if attribute_name not in product_attribute:
        product_attribute[attribute_name] = {}
    product_attribute[attribute_name] = attribute_values_dict
# _________________________________________________________________________________________________________
value_list1 = []
value_list2 = []
attribute_dict = {}
for prd_attr_id in sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]]):
    prd_attr = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [prd_attr_id])
    if prd_attr:
        prd_attr = prd_attr[0]
        attribute_dict.update({prd_attr.get('name', ''): prd_attr.get('id', '')})
# -----------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
for items in range(2, sheet_name.nrows):
    attribute_1 = sheet_name.cell_value(items, 2)
    attribute_2 = sheet_name.cell_value(items, 4)
    option_value_1 = sheet_name.cell_value(items, 3)
    option_value_2 = sheet_name.cell_value(items, 5)

     # atribute size created----------------------------------------
    if attribute_1 in attribute_dict:
        attribute_id = attribute_dict.get(attribute_1)
    else:
        attribute_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_1})])
        attribute_dict.update({attribute_1: attribute_id})
        product_attribute.update({attribute_1: {}})

    # attribute color created--------------------------------------------
    if attribute_2 in attribute_dict:
        attribute_2_id = attribute_dict.get(attribute_2)
    else:
        attribute_2_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_2})])
        attribute_dict.update({attribute_2: attribute_2_id})
        product_attribute.update({attribute_2: {}})

    # Attribute 1 value------------------------------------------------------------------------------------------------
    if attribute_1 and option_value_1:
        att1_all_values = product_attribute.get(attribute_1)
        if str(option_value_1) in att1_all_values:
            existing_attribute_id = att1_all_values[str(option_value_1)]
            attribute_vals = {'name': str(option_value_1), 'attribute_id': attribute_id}
            sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'write', [[existing_attribute_id], attribute_vals])
        else:
            new_attribute1_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                       [{'name': str(option_value_1), 'attribute_id': attribute_id}])
            product_attribute[attribute_1].update({str(option_value_1): new_attribute1_id})

    # Attribute 2 value----------------------------------------------------------------------------------
    if attribute_2 and option_value_2:
        att2_all_values =product_attribute.get(attribute_2)
        if str(option_value_2) in att2_all_values:
            existing_attribute_id = att2_all_values[str(option_value_2)]
            attribute_vals = {'name': str(option_value_2), 'attribute_id': attribute_2_id}
            sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'write',
                            [[existing_attribute_id], attribute_vals])
        else:
            new_attribute2_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                               [{'name': str(option_value_2), 'attribute_id': attribute_2_id}])
            # attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
            product_attribute[attribute_2].update({str(option_value_2): new_attribute2_id})

# ---------------------# product creation-----------------uom creation-------------------------------------------------------
    attr_1 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_1]]])
    attr_value1 = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search',
                                 [[['name', '=', str(option_value_1)], ['attribute_id','=', attr_1[0]]]])

    attr_2 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_2]]])
    attr_value2 = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search',
                                  [[['name', '=', str(option_value_2)], ['attribute_id', '=', attr_2[0]]]])
    uom_categ_rec = sock.execute_kw(dbname, uid, password, 'uom.category', 'search', [[['name', '=', 'Unit']]])

    if sheet_name.cell_value(items, 3):
        value_list1.append(attr_value1 and attr_value1[0])
    if sheet_name.cell_value(items, 5):
        value_list2.append(attr_value2 and attr_value2[0])

    uom_data = sheet_name.cell_value(items, 11).split(' ')
    uom_rec = sock.execute_kw(dbname, uid, password, 'uom.uom', 'search',
                              [[['name', '=', sheet_name.cell_value(items, 11)]]])
    uom_id = uom_rec
    if not uom_rec:
        uom_dict = {
            'name': sheet_name.cell_value(items, 11) or '',
            'uom_type': 'bigger',
            'ratio': uom_data and uom_data[0] or 0,
            'active': 't',
            'rounding': 0.01000,
            'category_id': uom_categ_rec and uom_categ_rec[0],
        }
        uom_rec_id = sock.execute_kw(dbname, uid, password, 'uom.uom', 'create', [uom_dict])
        uom_id = [uom_rec_id]

    if sheet_name.cell_value(items, 6):
        product_template_vals = {
            'default_code': sheet_name.cell_value(items, 0),
            'name': sheet_name.cell_value(items, 7),
            'barcode': sheet_name.cell_value(items, 14),
            'description': sheet_name.cell_value(items, 18),
            'description_sale': sheet_name.cell_value(items, 8),
            # 'image_1920': xmlrpclib.Binary(image_content),
            'sale_line_warn_msg': sheet_name.cell_value(items, 0),
            'uom_id': uom_id and uom_id[0],
            'uom_po_id': uom_id and uom_id[0],
            'detailed_type': 'product'
        }
        sock.execute_kw(dbname, uid, password, 'product.template', 'create', [product_template_vals])

    product_template = sock.execute_kw(dbname, uid, password, 'product.template', 'search',
                                       [[['sale_line_warn_msg', '=', sheet_name.cell_value(items, 0)]]])
    if product_template:
        default_code = sock.execute_kw(dbname, uid, password, 'product.template', 'read', product_template,
                                       {'fields': ['default_code']})
        if default_code and default_code[0].get('default_code') == sheet_name.cell_value(items, 0):
            if sheet_name.cell_value(items, 6) and attr_1 and value_list1 != []:
                sock.execute_kw(dbname, uid, password, 'product.template', 'write', [product_template, {
                    'attribute_line_ids': [(0, 0, {'attribute_id': attr_1[0], 'value_ids': [(6, 0, value_list1)]})]}])
                value_list1.clear()
            if sheet_name.cell_value(items, 6) and attr_2 and value_list2 != []:
                sock.execute_kw(dbname, uid, password, 'product.template', 'write', [product_template, {
                    'attribute_line_ids': [
                        (0, 0, {'attribute_id': attr_2[0], 'value_ids': [(6, 0, value_list2)]})]}])
                value_list2.clear()

# update barcode and reference
# ------------------------------------------------------------------------------------------------------------
for items in range(2, sheet_name.nrows):
    if not sheet_name.cell_value(items, 6):
        product_template = sock.execute_kw(dbname, uid, password, 'product.template', 'search', [[['sale_line_warn_msg', '=', sheet_name.cell_value(items, 0)]]])
        prod_recs = sock.execute_kw(dbname, uid, password, 'product.product', 'search', [[['product_tmpl_id', '=', product_template[0]]]])
        for prod in prod_recs:
            prod_tmp_var_att = sock.execute_kw(dbname, uid, password, 'product.product', 'read', [prod], {'fields': ['product_template_variant_value_ids']})
            if not prod_tmp_var_att[0].get('product_template_variant_value_ids') and str(sheet_name.cell_value(items, 3)) and str(sheet_name.cell_value(items, 5)):
                sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {'default_code': sheet_name.cell_value(items, 1), 'barcode': sheet_name.cell_value(items, 14)}])
                break
            prod_att_val = sock.execute_kw(dbname, uid, password, 'product.template.attribute.value', 'read',
                                           [prod_tmp_var_att[0].get('product_template_variant_value_ids')],
                                           {'fields': [str('product_attribute_value_id')]})

            size_found = False
            color_found = False
            both_value_same = False
            for pr_att in prod_att_val:
                att_val = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'read', [pr_att.get('product_attribute_value_id')[0]], {'fields': ['name']})

                if len(prod_att_val) > 1:
                    if str(att_val[0].get('name')) == str(sheet_name.cell_value(items, 3)):
                        size_found = True
                    if str(att_val[0].get('name')) == str(sheet_name.cell_value(items, 5)):
                        color_found = True
                else:
                    if att_val and att_val[0].get('name') == str(sheet_name.cell_value(items, 3)):
                        sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {
                            'default_code': sheet_name.cell_value(items, 1),
                            'barcode': sheet_name.cell_value(items, 14)}])
                        break
            if size_found and color_found:
                sock.execute_kw(dbname, uid, password, 'product.product', 'write', [[prod], {
                    'default_code': sheet_name.cell_value(items, 1),
                    'barcode': sheet_name.cell_value(items, 14)}])
                break

print('\n\n!!!!!!!!! END Script Execution', datetime.now())

