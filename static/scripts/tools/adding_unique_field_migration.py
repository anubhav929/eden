import os
import sys
import copy
import subprocess
import mapping

WEB2PY_PATH = sys.argv[1]
APP = sys.argv[2]
changed_table = "org_organisation"
new_unique_field = "NewField"

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


database_string = "sqlite://storage.db"
old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)

#MIGRATION SCRIPT


new_field = Field(new_unique_field,"integer")

try:
    changed_table_primary_key = db[changed_table]._primarykey
except KeyError:
    changed_table_primary_key = None

print db[changed_table]

temp_db.define_table(changed_table ,db[changed_table],new_field,primarykey = changed_table_primary_key)
temp_db.define_table("org_organisation_type" ,db["org_organisation_type"])
mapping.setfields(db)

for row in temp_db().select(db[changed_table].ALL):
    changed_value = mapping.mapping(temp_db(mapping.query).select(*mapping.fields))
    print changed_value
    eval("temp_db(temp_db[changed_table][\"id\"] == row[\"id\"]).update(%s = changed_value)" %(new_unique_field))

temp_db.commit()
temp_db = {}

temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
new_field = Field(new_unique_field,"integer",notnull = True , unique = True)

try:
    changed_table_primary_key = db[changed_table]._primarykey
except KeyError:
    changed_table_primary_key = None

temp_db.define_table(changed_table ,db[changed_table],new_field,primarykey = changed_table_primary_key)
temp_db.commit()
