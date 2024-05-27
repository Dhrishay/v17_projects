from xmlrpc import client as xmlrpclib
import xlrd
import base64
import requests

username = 'admin' #the user
password = 'admin'      #the password of the user
dbname = 'v17_product_import_test_new_1403'
server = 'http://0.0.0.0:8082/'

sock_common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % server)
uid = sock_common.login(dbname, username, password)
sock = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % server, allow_none=True)
print("\n\nsock:::::::::::>>>>>>>>>>", sock)

wb = xlrd.open_workbook('/tmp/Customer_Product_Download_Ross_Final.xlsx')
sheet_name = wb.sheet_by_name('AnthonyWebstoreResults')

# create a code for existing attribute and value already in database
product_attribute = {}
product_attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]])
print("product_attribute_data--------------------------",product_attribute_data)
for att_id in product_attribute_data:
    attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [att_id])
    attribute_name = attribute_data[0]['name']
    existing_value_ids = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search_read', [[('attribute_id', '=', att_id)]], {'fields': ['name', 'id']})
    attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
    print("attribute_values_dict--------22222222----------------------",attribute_values_dict)
    if attribute_name not in product_attribute:
        product_attribute[attribute_name] = {}

    product_attribute[attribute_name] = attribute_values_dict
    print("attribute_name_to_id[attribute_name]---------33333333333--------------",product_attribute[attribute_name])
print("attribute_name_to_id------????????????---------------------",product_attribute)

value_list = []
attribute_dict = {}
product_attribute = {}
attr_value_dict = {}
for prd_attr_id in sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]]):
    prd_attr = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [prd_attr_id])
    print("\n\nprd_attr===>>>>>>>>", prd_attr)
    if prd_attr:
        prd_attr = prd_attr[0]
        attribute_dict.update({prd_attr.get('name', ''): prd_attr.get('id', '')})
        print("attribute_dict--------------------",attribute_dict)

prod_att_ids = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search', [[]])
att_rec = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'read', [prod_att_ids], {'fields': ['name','id','attribute_id']})
for attr in att_rec:
    attribute_id = attr.get('attribute_id')[0]
    print("attr------------------------------",attr)
    product_att = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [attribute_id], {'fields': ['name']})
    print("product_att--------------------------------",product_att)

    if product_att[0].get('name') in product_attribute:
        product_attribute.get(product_att[0].get('name')).update({attr.get('name'): attr.get('id')})
        print("product_attribute------------1111---------------",product_attribute)
    else:
        product_attribute.update({product_att[0].get('name'): {attr.get('name'): attr.get('id')}})
        print("product_attribute-------------2222222-----------------",product_attribute)

for items in range(2, sheet_name.nrows):
    attribute_1 = sheet_name.cell_value(items, 2)
    attribute_2 = sheet_name.cell_value(items, 4)
    option_value_1 = sheet_name.cell_value(items, 3)
    option_value_2 = sheet_name.cell_value(items, 5)

    attr_value = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search', [[['name', '=', str(option_value_1)]]])
    uom_categ_rec = sock.execute_kw(dbname, uid, password, 'uom.category', 'search', [[['name', '=', 'Unit']]])

    # attribute size create--------------------------------
    if attribute_1 in attribute_dict:
        prd_attr_id = attribute_dict.get(attribute_1)
    else:
        prd_attr_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_1})])
        attribute_dict.update({attribute_1: prd_attr_id})
        print("attribute_dict--------------->>>>>>>--------------", attribute_dict)

    # attribute color create---------------------------------------
    if attribute_2 in attribute_dict:
        prd_attr_id = attribute_dict.get(attribute_1)
    else:
        prd_attr_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_2})])
        attribute_dict.update({attribute_2: prd_attr_id})

    att_id1 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_1]]])
    print("att_id1=--------------------------", att_id1)
    if option_value_1:
        print("\n\noption_value_1:::::::><>>>>>>", option_value_1)
        if option_value_1 in attr_value_dict:
            value_id = attr_value_dict.get(option_value_1)
        else:
            value_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                       [({'name': option_value_1, 'attribute_id': att_id1[0]})])
            attr_value_dict.update({option_value_1: value_id})
            print("attr_value_dict------------------222222---------------", attr_value_dict)

    att_id2 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_2]]])
    if option_value_2:
        if option_value_2 in attr_value_dict:
            value_id = attr_value_dict.get(option_value_2)
        else:
            value_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                       [({'name': option_value_2, 'attribute_id': att_id2[0]})])
            attr_value_dict.update({option_value_2: value_id})
            print("attr_value_dict-------------222222------------------", attr_value_dict)

att_dict = {}

for item in range(2, sheet_name.nrows):
    product_tem_name = sheet_name.cell_value(item, 0)
    attribute_1 = sheet_name.cell_value(item, 2)
    attribute_2 = sheet_name.cell_value(item, 4)
    option_value_1 = sheet_name.cell_value(item, 3)
    option_value_2 = sheet_name.cell_value(item, 5)

    if product_tem_name not in att_dict:
        att_dict[product_tem_name] = [{
            attribute_1: [product_attribute.get(attribute_1, {}).get(option_value_1)],
            attribute_2: [product_attribute.get(attribute_2, {}).get(option_value_2)]
        }]
    else:
        if attribute_1 in att_dict[product_tem_name][0] and \
           product_attribute.get(attribute_1, {}).get(option_value_1) not in att_dict[product_tem_name][0][attribute_1]:
            att_dict[product_tem_name][0][attribute_1].append(product_attribute.get(attribute_1, {}).get(option_value_1))
        if attribute_2 in att_dict[product_tem_name][0] and \
           product_attribute.get(attribute_2, {}).get(option_value_2) not in att_dict[product_tem_name][0][attribute_2]:
            att_dict[product_tem_name][0][attribute_2].append(product_attribute.get(attribute_2, {}).get(option_value_2))

print('\n\n:::::::Script Execute Successfully')

