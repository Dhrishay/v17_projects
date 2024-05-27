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
# ---------------------------------------------------------------------------------------------------
product_attribute = {}
product_attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]])
# print("product_attribute_data--------------------------",product_attribute_data)
for att_id in product_attribute_data:
    attribute_data = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [att_id])
    attribute_name = attribute_data[0]['name']
    existing_value_ids = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'search_read', [[('attribute_id', '=', att_id)]], {'fields': ['name', 'id']})
    attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
    # print("attribute_values_dict--------22222222----------------------",attribute_values_dict)
    if attribute_name not in product_attribute:
        product_attribute[attribute_name] = {}

    product_attribute[attribute_name] = attribute_values_dict
    # print("product_attribute[attribute_name]---------33333333333--------------",product_attribute[attribute_name])
# print("product_attribute------????????????---------------------",product_attribute)
# _________________________________________________________________________________________________________

value_list = []
attribute_dict = {}
for prd_attr_id in sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[]]):
    prd_attr = sock.execute_kw(dbname, uid, password, 'product.attribute', 'read', [prd_attr_id])
    # print("\n\nprd_attr===>>>>>>>>", prd_attr)
    if prd_attr:
        prd_attr = prd_attr[0]
        attribute_dict.update({prd_attr.get('name', ''): prd_attr.get('id', '')})
        # print("attribute_dict--------------------",attribute_dict)
# -----------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------
for items in range(2, sheet_name.nrows):
    attribute_1 = sheet_name.cell_value(items, 2)
    attribute_2 = sheet_name.cell_value(items, 4)
    option_value_1 = sheet_name.cell_value(items, 3)
    option_value_2 = sheet_name.cell_value(items, 5)
    print("\n\noption_value_21111::::::>>>>>>>>>", attribute_1, option_value_1, attribute_2, option_value_2)

     # atribute size created----------------------------------------
    if attribute_1 in attribute_dict:
        attribute_id = attribute_dict.get(attribute_1)
    else:
        attribute_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_1})])
        attribute_dict.update({attribute_1: attribute_id})
        # print("attribute_dict--------------->>>>>>>--------------", attribute_dict)

    # attribute color created--------------------------------------------
    if attribute_2 in attribute_dict:
        attribute_2_id = attribute_dict.get(attribute_2)
    else:
        attribute_2_id = sock.execute_kw(dbname, uid, password, 'product.attribute', 'create', [({'name': attribute_2})])
        attribute_dict.update({attribute_2: attribute_2_id})

    # att_id1 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_1]]])
    # print("att_id1---------------------------------",att_id1)
    # att_id2 = sock.execute_kw(dbname, uid, password, 'product.attribute', 'search', [[['name', '=', attribute_2]]])
    # print("att_id2---------------------------------",att_id2)
    # aaaaaaaaaaaaaaaaaaaaaaaaaaaaa

    # Attribute 1
    if attribute_1 and option_value_1:
        att1_all_values = product_attribute.get(attribute_1)
        # print("att1_all_values------------------------------",att1_all_values)
        if str(option_value_1) in att1_all_values:
            # TODO: Update
            existing_attribute_id = att1_all_values[str(option_value_1)]
            attribute_vals = {'name': str(option_value_1), 'attribute_id': attribute_id}
            sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'write',
                            [[existing_attribute_id], attribute_vals])
        else:
            # TODO: Create
            new_attribute1_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                       [{'name': str(option_value_1), 'attribute_id': attribute_id}])
            # attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
            product_attribute[attribute_1].update({str(option_value_1): new_attribute1_id})

    # Attribute 2
    if attribute_2 and option_value_2:
        att2_all_values = product_attribute.get(attribute_2)
        print("\n\nproduct_attribute:::::::>>>>>>",option_value_2,  product_attribute)
        if str(option_value_2) in att2_all_values:
            # TODO: Update
            existing_attribute_id = att2_all_values[str(option_value_2)]
            attribute_vals = {'name': str(option_value_2), 'attribute_id': attribute_2_id}
            sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'write',
                            [[existing_attribute_id], attribute_vals])
        else:
            # TODO: Create
            new_attribute2_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
                                               [{'name': str(option_value_2), 'attribute_id': attribute_2_id}])
            # attribute_values_dict = {value['name']: value['id'] for value in existing_value_ids}
            product_attribute[attribute_2].update({str(option_value_2): new_attribute2_id})




    # option_value_1_exists = False
    # if str(option_value_1):
    #     for attribute_values in product_attribute.values():
    #         print("attribute_values---------------------------------",attribute_values)
    #         if str(option_value_1) in attribute_values:
    #             # print("option_value_1-------------------------------",option_value_1)
    #             option_value_1_exists = True
    #             # print("option_value_1_exists-------------------------------",option_value_1_exists)
    #             break
    #     if option_value_1_exists:
    #         print("if************************")
    #         existing_value_id = product_attribute[attribute_1][str(option_value_1)]
    #         # print("existing_value_id------------------------",existing_value_id)
    #         print("option_value_1------------111111111111----------------------",str(option_value_1))
    #         print("attribute_id------------111111111111----------------------",attribute_id)
    #         updated_value_data = {'name': str(option_value_1), 'attribute_id': attribute_id}
    #         # print("updated_value_data--------------------------",updated_value_data)
    #         sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'write',
    #                         [[existing_value_id], updated_value_data])
    #     else:
    #         print("else **************************************************")
    #         print("Attribute value does not exist. Creating...")
    #         print("option_value_1--------------------------",str(option_value_1))
    #         print("attribute_id--------------------------",attribute_id)
    #         # Create a new attribute value in the database
    #         value_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
    #                                    [{'name': str(option_value_1), 'attribute_id': attribute_id}])
    #         # value_list.append({'name': option_value_1, 'attribute_id': attribute_id})
    #         # value_id = sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create', value_list)
    #         print("value_id---------------------------------",value_id)
    #         # Update the product_attribute dictionary with the new attribute value
    #         product_attribute.setdefault(attribute_1, {})[str(option_value_1)] = value_id
    #         print("product_attribute updated:", product_attribute)



            # sock.execute_kw(dbname, uid, password, 'product.attribute.value', 'create',
            #                 value_list)


print('\n\n:::::::Script Execute Successfully')

