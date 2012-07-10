import os
import sys
import copy
import subprocess

own_path = os.path.realpath(__file__)
own_path = own_path.split(os.path.sep)
index_application = own_path.index("applications")
WEB2PY_PATH = (os.path.sep).join(own_path[0:index_application])
APP = "eden"
changed_table = "org_organisation"
new_field = "type_id"
new_table = "org_organisation_type"
old_field = "type"
new_table_field = "name"

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
db = db
'''
d = globals().copy()
d.update(**old_env)
exec old_str in d, locals()

d.clear()

database_string = "sqlite://storage.db"
old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)

#MIGRATION SCRIPT

list_of_fields = []
list_of_fields.append(Field(new_field,"integer"))

list_of_new_table_fields = []
list_of_new_table_fields.append(Field(new_table_field,"integer"))

temp_db.define_table(changed_table ,db[changed_table],*list_of_fields)
temp_db.define_table(new_table , *list_of_new_table_fields)

temp_db.commit()

#Adding a new field of int type in a class

for old_row in temp_db().select(temp_db[changed_table][old_field]):
    if (len(temp_db(temp_db[new_table][new_table_field] == old_row[old_field]).select()) == 0):
        temp_db[new_table].insert(name = old_row[old_field])
    new_id = int(temp_db(temp_db[new_table][new_table_field] == old_row[old_field]).select(temp_db[new_table]["id"])[0]["id"])
    temp_db(temp_db[changed_table][old_field] == old_row[old_field]).update(type_id = new_id)
    
temp_db.commit()
