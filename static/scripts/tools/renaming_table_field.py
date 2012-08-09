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
    driver = ""
    if settings.database.db_type:
        dbengine = settings.database.db_type
    return [db,dbengine]

def renaming_table(db,old_table_name,new_table_name):
    try:
        db.executesql("ALTER TABLE %s  RENAME TO %s;" % (old_table_name, new_table_name))
    except Exception:
        print "Exception given in renaming_table_function"     
    db.commit()

def adding_renamed_fields(db,table_name,old_field_name,new_field_name,attributes_to_copy):
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
    new_field = Field(new_field_name)
    try:
        table_primary_key = db[table_name]._primarykey
    except KeyError:
        table_primary_key = None
    for attribute in attributes_to_copy:
        exec_str = "db[table_name][old_field_name].%(attribute)s = new_field.%(attribute)s" % {"attribute":attribute}
        exec exec_str in globals() , locals()
    temp_db.define_table(table_name ,db[table_name],new_field,primarykey = table_primary_key)
    return temp_db

def copy_field(db,table_name,old_field_name,new_field_name):
    dict_update = {}
    for row in db().select(db[table_name][old_field_name]):
        dict_update[new_field_name] = row[old_field_name]
        db(db[table_name][old_field_name] == row[old_field_name]).update(**dict_update)
    return db


def map_type(dal_type):
    if dal_type == "string":
        return "varchar"
    else:
        return dal_type

def renaming_field(db,table_name,old_field_name,new_field_name,attributes_to_copy = None,dbengine="sqlite"):
    if dbengine == "sqlite":
        db = copy_field(db,table_name,old_field_name,new_field_name)     
        list_index = db.executesql("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='%s' ORDER BY name;" %(table_name))
        for element in list_index:
            if element[0] is not None and "%s(%s)" % (table_name,old_field_name) in element[0]:
                db.executesql("CREATE INDEX %s__idx on %s(%s);" % (new_field_name, table_name,new_field_name))
    elif dbengine == "mysql":
        sql_type = map_type(db[table_name][old_field_name].type)
        query = "ALTER TABLE %s CHANGE %s %s %s(%s)" % (table_name,old_field_name,new_field_name,sql_type,db[table_name][old_field_name].length)
        db.executesql(query)
    else :
        query = "ALTER TABLE %s RENAME COLUMN %s TO %s" % (table_name,old_field_name,new_field_name)
        db.executesql(query)
    db.commit()


attributes_to_copy = ["type","length","default","required","requires","ondelete","notnull","unique",
        "uploadfield","widget","label","comment","writable","readable","update","authorize",
        "autodelete","represent","uploadfolder","uploadseparate","uploadfs","compute","custom_store",
        "custom_retrieve","custom_retrieve_file_properties","custom_delete","filter_in","filter_out"]
        
dbengine = ""
[db,dbengine] = get_old_db()
if not dbengine:
    dbengine = "sqlite"
renaming_field(db,"pr_person","first_name","renamed_person2",attributes_to_copy,dbengine)
renaming_table(db,"renamed_vehicle","vehicle_vehicle")
