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
    dbengine = ""
    if settings.database.db_type:
        dbengine = settings.database.db_type
    return [db,dbengine]

def map_type(old_type):
    if ((old_type == "list:integer") or (old_type.startswith("list:reference"))):
        return "integer"
    elif old_type == "list:string":
        return "string"

def creating_new_table(db , new_table_name , new_list_field , list_field_name , old_table_id_field , old_table,list_referncing_table = None):
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
    new_field_type = map_type(db[old_table][list_field_name].type)
    new_field = Field(new_list_field,new_field_type)
    new_id_field = Field("%s_%s" %(old_table,old_table_id_field),"integer")
    temp_db.define_table(new_table_name ,new_id_field , new_field )
    temp_db.define_table(old_table ,db[old_table])
    if list_referncing_table:
        temp_db.define_table(list_referncing_table ,db[list_referncing_table])  
    temp_db.commit()
    return temp_db

def fill_the_new_table(db , new_table_name , new_list_field , list_field_name , old_table_id_field , old_table ):
    update_dict = {}
    for row in db().select(db[old_table][old_table_id_field],db[old_table][list_field_name]):
        for element in row[list_field_name]:
            update_dict[new_list_field] = element
            update_dict["%s_%s" %(old_table,old_table_id_field)] = row[old_table_id_field]
            db[new_table_name].insert(**update_dict)
    temp_db.commit()
    
        
dbengine = ""
[db,dbengine] = get_old_db()
if not dbengine:
    dbengine = "sqlite"

new_table_name = "sector_id_reference"
new_list_field = list_field_name = "sector_id"
old_table_id_field = "id"
old_table = "org_organisation"
list_referncing_table = "org_sector"

db = creating_new_table(db , new_table_name , new_list_field , list_field_name , old_table_id_field , old_table,list_referncing_table)
fill_the_new_table(db , new_table_name , new_list_field , list_field_name , old_table_id_field , old_table )
