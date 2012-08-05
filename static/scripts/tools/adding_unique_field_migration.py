import os
import sys
import copy
import subprocess

# GETTING CONSTANTS

WEB2PY_PATH = sys.argv[1]
APP = sys.argv[2]


def get_old_db():
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
    return db

def adding_new_fields(db,new_unique_field,changed_table):
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
    new_field = Field(new_unique_field,"integer")
    try:
        changed_table_primary_key = db[changed_table]._primarykey
    except KeyError:
        changed_table_primary_key = None
    temp_db.define_table(changed_table ,db[changed_table],new_field,primarykey = changed_table_primary_key)
    temp_db.define_table("org_organisation_type" ,db["org_organisation_type"])
    return temp_db


def update_with_mappings(db,changed_table,field_to_update,mapping_function):
    fields = mapping_function.fields(db)
    if db[changed_table]["id"] not in fields:
        fields.append(db[changed_table]["id"])
    exec_str="db(db[changed_table][\"id\"] == row_id).update(%s = changed_value)" % (field_to_update)
    rows = db(mapping_function.query(db)).select(*fields)
    if rows:
        try:
                rows[0][changed_table]["id"]
                row_single_layer = False
        except KeyError:
                row_single_layer = True
    for row in rows:
        if not row_single_layer:
            row_id = row[changed_table]["id"]
        else:
            row_id = row["id"]
        changed_value = mapping_function.mapping(row)
        exec exec_str in globals(), locals()    
    db.commit()

# CALLING GENERAL FUNCTIONS
field_to_update = "NewField"
changed_table = "org_organisation"

import mapping_function

db = get_old_db()
db = adding_new_fields(db,field_to_update,changed_table)
update_with_mappings(db,changed_table,field_to_update,mapping_function)
