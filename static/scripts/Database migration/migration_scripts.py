import os
import sys
import copy
import subprocess

# GETTING CONSTANTS
WEB2PY_PATH = APP = dbengine = ""
db = {}

def set_globals(web2py_path,app):
    global WEB2PY_PATH,APP,dbengine
    WEB2PY_PATH = web2py_path
    APP = app
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
    if settings.database.db_type:
        dbengine = settings.database.db_type
    else:
        dbengine = "sqlite"

def map_type_list_field(old_type):
    if (old_type == "list:integer"):
        return "integer"
    elif old_type.startswith("list:reference"):
        return old_type.strip("list:")
    elif old_type == "list:string":
        return "string"

def creating_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table): 
    new_field_type = map_type_list_field(db[old_table][list_field_name].type)
    new_field = Field(new_list_field,new_field_type)
    new_id_field = Field("%s_%s" %(old_table,old_table_id_field),"reference %s" % ( old_table))
    db.define_table(new_table_name ,new_id_field , new_field )
    db.commit()
    
def fill_the_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table ):
    update_dict = {}
    for row in db().select(db[old_table][old_table_id_field],db[old_table][list_field_name]):
        for element in row[list_field_name]:
            update_dict[new_list_field] = element
            update_dict["%s_%s" %(old_table,old_table_id_field)] = row[old_table_id_field]
            db[new_table_name].insert(**update_dict)
    db.commit()

def renaming_table(old_table_name,new_table_name):
    try:
        db.executesql("ALTER TABLE %s  RENAME TO %s;" % (old_table_name, new_table_name))
    except Exception:
        print "Exception given in renaming_table_function"     
    db.commit()

def adding_renamed_fields(table_name,old_field_name,new_field_name,attributes_to_copy):
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
    new_field = Field(new_field_name)
    try:
        table_primary_key = db[table_name]._primarykey
    except KeyError:
        table_primary_key = None
    for attribute in attributes_to_copy:
        exec_str = "new_field.%(attribute)s = db[table_name][old_field_name].%(attribute)s" % {"attribute":attribute}
        exec exec_str in globals() , locals()
    temp_db.define_table(table_name ,db[table_name],new_field,primarykey = table_primary_key)
    return temp_db

def copy_field(table_name,old_field_name,new_field_name):
    dict_update = {}
    for row in db().select(db[table_name][old_field_name]):
        dict_update[new_field_name] = row[old_field_name]
        db(db[table_name][old_field_name] == row[old_field_name]).update(**dict_update)
    return db


def map_type_web2py_to_sql(dal_type):
    if dal_type == "string":
        return "varchar"
    else:
        return dal_type

def renaming_field(table_name,old_field_name,new_field_name,attributes_to_copy = None,dbengine="sqlite"):
    if dbengine == "sqlite":
        db = adding_renamed_fields(table_name,old_field_name,new_field_name,attributes_to_copy)
        db = copy_field(table_name,old_field_name,new_field_name)     
        list_index = db.executesql("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='%s' ORDER BY name;" %(table_name))
        for element in list_index:
            if element[0] is not None and "%s(%s)" % (table_name,old_field_name) in element[0]:
                db.executesql("CREATE INDEX %s__idx on %s(%s);" % (new_field_name, table_name,new_field_name))
    elif dbengine == "mysql":
        sql_type = map_type_web2py_to_sql(db[table_name][old_field_name].type)
        query = "ALTER TABLE %s CHANGE %s %s %s(%s)" % (table_name,old_field_name,new_field_name,sql_type,db[table_name][old_field_name].length)
        db.executesql(query)
    elif dbengine == "postgres" :
        query = "ALTER TABLE %s RENAME COLUMN %s TO %s" % (table_name,old_field_name,new_field_name)
        db.executesql(query)
    db.commit()


def adding_new_fields(new_unique_field,changed_table):
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    temp_db = DAL( database_string, folder = old_database_folder, migrate_enabled=True ,migrate = True)
    new_field = Field(new_unique_field,"integer")
    try:
        changed_table_primary_key = db[changed_table]._primarykey
    except KeyError:
        changed_table_primary_key = None
    temp_db.define_table(changed_table ,db[changed_table],new_field,primarykey = changed_table_primary_key)
    return temp_db

def adding_tables_temp_db(temp_db , list_of_table):
    for table in list_of_table:
		temp_db.define_table(table ,db[table])
    return temp_db

def update_with_mappings(changed_table,field_to_update,mapping_function):
    fields = mapping_function.fields(db)
    if db[changed_table]["id"] not in fields:
        fields.append(db[changed_table]["id"])
    rows = db(mapping_function.query(db)).select(*fields)
    if rows:
        try:
                rows[0][changed_table]["id"]
                row_single_layer = False
        except KeyError:
                row_single_layer = True
    dict_update = {}
    for row in rows:
        if not row_single_layer:
            row_id = row[changed_table]["id"]
        else:
            row_id = row["id"]
        changed_value = mapping_function.mapping(row)
        dict_update[field_to_update] = changed_value
        db(db[changed_table]["id"] == row_id).update(**dict_update)    
    db.commit()

