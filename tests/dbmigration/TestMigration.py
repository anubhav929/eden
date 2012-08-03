import os
import sys
import subprocess

own_path = os.path.realpath(__file__)
own_path = own_path.split(os.path.sep)
index_application = own_path.index("applications")
CURRENT_EDEN_APP  = own_path[index_application + 1]
WEB2PY_PATH = (os.path.sep).join(own_path[0:index_application])
APP = "eden"
changed_table = "org_organisation"
new_field = "type_id"
old_field = "type"
new_table_field = "name"
new_table = "org_organisation_type"
file_to_test = sys.argv[1]

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


for a in range(10):
    db[changed_table].insert(name = "test_%s" %(str(a)), organisation_type_id = a%5 , uuid = "%s%s" %(db[changed_table]["uuid"].default,str(a)))

db.commit()
subprocess.call("python %s/applications/%s/static/scripts/tools/%s.py %s %s" % \
         (WEB2PY_PATH, CURRENT_EDEN_APP,file_to_test, WEB2PY_PATH, APP) , shell =True )

"""
Retreiving Data
"""

database_string = "sqlite://storage.db"
old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
db = DAL( database_string, folder = old_database_folder, auto_import = True, migrate_enabled=True ,migrate = True)

print "CHANGED TABLE :"
for row in db(db[changed_table]).select():
    print "name = ",row["name"],"old_field = ",row[old_field],"new_field = ",row[new_field]

print "NEW TABLE :"
for row in db(db[new_table]).select():
    print "name = ",row[new_table_field],"id = ",row["id"]
