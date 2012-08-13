import os
import sys
import subprocess


own_path = os.path.realpath(__file__)
own_path = own_path.split(os.path.sep)
index_application = own_path.index("applications")
CURRENT_EDEN_APP  = own_path[index_application + 1]
WEB2PY_PATH = (os.path.sep).join(own_path[0:index_application])
APP = "eden"
new_table_name = "sector_id_reference"
new_list_field = list_field_name = "sector_id"
old_table_id_field = "id"
old_table = "org_organisation"

os.chdir(WEB2PY_PATH)
sys.path.append(WEB2PY_PATH)

from gluon.custom_import import custom_import_install
custom_import_install(WEB2PY_PATH)
from gluon.shell import env
from gluon import DAL, Field
old_env = env(APP, c=None, import_models=True)
old_str ='''
try:
    s3db.load_all_models()
except NameError:
    print "s3db not defined"
'''
globals().update(**old_env)
exec old_str in globals(), locals()



for a in range(2,10):
    db[old_table].insert(name = "test_%s" %(str(a)), organisation_type_id = a%5 , uuid = "%s%s" %(db[old_table]["uuid"].default,str(a)),sector_id = [a-2,a-1,a])

db.commit()

subprocess.call("python %s/applications/%s/static/scripts/tools/list_fields_to_references.py %s %s" % \
         (WEB2PY_PATH, CURRENT_EDEN_APP, WEB2PY_PATH, APP) , shell =True )

"""
Retreiving Data
"""

database_string = "sqlite://storage.db"
old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
db = DAL( database_string, folder = old_database_folder, auto_import = True, migrate_enabled=True ,migrate = True)

print old_table
for row in db(db[old_table]).select():
	print "id = ",row[old_table_id_field],"sector_id = ",row[list_field_name]

print new_table_name
for row in db(db[new_table_name]).select():
    print "id = ",row["%s_%s" %(old_table,old_table_id_field)],"sector_id = ",row[new_list_field]
