from xmlrpc import client as xmlrpclib

username = 'admin' #the user
password = 'admin'      #the password of the user
dbname = 'v17_product_import_test_new_1403'
server = 'http://0.0.0.0:8082/'

# sock_common = xmlrpclib.ServerProxy('https://'+ server +'/xmlrpc/2/common')
sock_common = xmlrpclib.ServerProxy('%s/xmlrpc/2/common' % server)
uid = sock_common.login(dbname, username, password)
sock = xmlrpclib.ServerProxy('%s/xmlrpc/2/object' % server, allow_none=True)
print("\n\nsock:::::::::::>>>>>>>>>>", sock)

sock.execute_kw(dbname, uid, password, 'res.company', 'import_products', [1])
print('\n\n:::::::Script Execute Successfully')
