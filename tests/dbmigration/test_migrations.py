import os
import sys

own_path = os.path.realpath(__file__)
own_path = own_path.split(os.path.sep)
index_application = own_path.index("applications")
CURRENT_APP_PATH  = (os.path.sep).join(own_path[0:index_application+2])
WEB2PY_PATH = (os.path.sep).join(own_path[0:index_application])
APP = "eden"

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

def get_migrated_db():
    os.chdir(WEB2PY_PATH)
    sys.path.append(WEB2PY_PATH)
    from gluon import DAL, Field
    database_string = "sqlite://storage.db"
    old_database_folder = "%s/applications/%s/databases" % (WEB2PY_PATH, APP)
    db = DAL( database_string, folder = old_database_folder, auto_import = True, migrate_enabled=True ,migrate = True)
    return db


migration_sample_path = (os.path.sep).join([CURRENT_APP_PATH,"static","scripts","Database migration"])
sys.path.insert(0, migration_sample_path)
import migration_scripts

def list_field_to_reference(web2py_path,app):
    new_table_name = "sector_id_reference"
    new_list_field = list_field_name = "sector_id"
    old_table_id_field = "id"
    old_table = "org_organisation"
    db = get_old_db()
    for a in range(2,10):
        db[old_table].insert(name = "test_%s" %(str(a)), organisation_type_id = a%5 , uuid = "%s%s" %(db[old_table]["uuid"].default,str(a)),sector_id = [a-2,a-1,a])
    db.commit()
    migration_scripts.list_field_to_reference(web2py_path,app,new_table_name , new_list_field , list_field_name , old_table_id_field , old_table)
    db = get_migrated_db()
    print old_table
    for row in db(db[old_table]).select():
        print "id = ",row[old_table_id_field],"sector_id = ",row[list_field_name]
    print new_table_name
    for row in db(db[new_table_name]).select():
        print "id = ",row["%s_%s" %(old_table,old_table_id_field)],"sector_id = ",row[new_list_field]
    

def renaming_field(web2py_path,app):
    db = get_old_db()
    old_table = "pr_person"
    print old_table
    for row in db(db[old_table]).select():
        print "id = ",row["id"],"first_name = ",row["first_name"]
    attributes_to_copy = ["type","length","default","required","requires","ondelete","notnull","unique",
            "uploadfield","widget","label","comment","writable","readable","update","authorize",
            "autodelete","represent","uploadfolder","uploadseparate","uploadfs","compute","custom_store",
            "custom_retrieve","custom_retrieve_file_properties","custom_delete","filter_in","filter_out"]        
    migration_scripts.migration_renaming_field(web2py_path, app, old_table, "first_name", "first_name_pr",attributes_to_copy)
    db = get_migrated_db()
    print old_table
    for row in db(db[old_table]).select():
        print "id = ",row["id"],"first_name_pr = ",row["first_name_pr"]
    

def renaming_table(web2py_path,app):
    migration_scripts.migration_renaming_table(web2py_path,app,"vehicle_vehicle","rename_vehicle")
    

def adding_new_field(web2py_path,app):
    field_to_update = "NewField3"
    changed_table = "org_organisation"
    migration_scripts.migrating_to_unique_field(web2py_path,app,field_to_update,changed_table,["org_organisation_type","org_sector"])
    db = get_migrated_db()
    for row in db(db[changed_table]).select():
        print "id = ",row["id"],field_to_update," = ",row[field_to_update]
    


prt_str = '''
Select the migration that you wanto test
1.List field to table
2.Renaming field
3.Renaming Table
4.Addding a unique field

to test specific migration script call TestMigration.py   
'''
print prt_str
option_chosen = int(raw_input())
if option_chosen == 1:
    list_field_to_reference(WEB2PY_PATH,APP)

elif option_chosen == 2:
    renaming_field(WEB2PY_PATH,APP)

elif option_chosen == 3:
    renaming_table(WEB2PY_PATH,APP)

elif option_chosen == 4:
    adding_new_field(WEB2PY_PATH,APP)

